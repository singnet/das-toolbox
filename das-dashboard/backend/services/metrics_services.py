import asyncio
import json
from collections import defaultdict
from datetime import datetime, timezone

from shared.enums.metric_scope import MetricScope
from shared.enums.metrics_period import MetricsPeriod
from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH, LOCAL_HOSTS
from shared.internal.background_services_control import BackgroundServicesControl
from shared.exceptions.custom_exceptions import DasCliNotInstalledException, CustomValueError
from shared.db.metrics_db import (
    save_service_metrics_data,
    delete_metrics_by_ip,
    delete_unused_metrics,
    delete_all_metrics,
    get_service_metrics_averages,
    HISTORY_CHUNK_COUNT,
    PERIOD_SECONDS,
)
from shared.utils.das_cli_response import (
    clean_cli_output,
    parse_das_cli_stdout,
    raise_from_cli_output,
)

METRICS_COLLECTION_JOB = "metrics_collection"


class MetricsServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config
        self.job_control = BackgroundServicesControl()

    def _remote_host_ips(self) -> list[str]:
        if not self.web_config.config_dictionary:
            return []

        return [
            server["ip"]
            for server in self.web_config.map_dashboard_hosts()
            if server.get("ip")
        ]

    def _require_configured_host(self, server_ip: str) -> None:
        if server_ip not in self._remote_host_ips():
            raise CustomValueError(
                "Specified server ip is not present on the configuration file. "
                "Non-configured servers are prone to error and any data collected won't be displayed."
            )

    ## Main services (run fetching real time data)

    async def _start_cli(self, host: str, *, stream: bool = False):
        cmd = ["das-cli", "system", "status"]

        if host not in LOCAL_HOSTS:
            profile = self.web_config.user_profile
            ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH
            cmd.extend([
                "--remote",
                "--host", host,
                "-u", profile.get("profile_username", "root"),
                "-k", ssh_key,
            ])

        if stream:
            cmd.append("--stream")

        cmd.extend(["-o", "json"])

        try:
            return await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except FileNotFoundError:
            raise DasCliNotInstalledException("das-cli not found.")

    def _scoped_payload(self, metric_scope: MetricScope, parsed, host: str) -> dict:
        server_json = parsed[0] if isinstance(parsed, list) and parsed else parsed

        if not isinstance(server_json, dict):
            return {"ip": host, "type": "error", "message": str(server_json)}

        if metric_scope == MetricScope.SERVER:
            return {"ip": host, "machineInfo": server_json.get("machineInfo", {})}

        if metric_scope == MetricScope.SERVICE:
            return {"ip": host, "serviceInfo": server_json.get("serviceInfo", {})}

        return {"ip": host, **server_json}

    async def load_server_metrics(self, metric_scope: MetricScope, host: str):
        process = await self._start_cli(host)
        stdout, _ = await process.communicate()
        cleaned_stdout = clean_cli_output(stdout.decode())

        if process.returncode:
            raise_from_cli_output(
                cleaned_stdout,
                default_message="Failed to load server metrics.",
                exit_code=process.returncode,
            )

        try:
            parsed_json = parse_das_cli_stdout(cleaned_stdout)
        except json.JSONDecodeError:
            raise_from_cli_output(
                cleaned_stdout,
                default_message="Failed to load server metrics.",
                exit_code=process.returncode,
            )

        return self._scoped_payload(metric_scope, parsed_json, host)

    async def stream_server_metrics(self, metric_scope: MetricScope, host: str):
        process = await self._start_cli(host, stream=True)

        try:
            async for line_bytes in process.stdout:
                cleaned_line = clean_cli_output(line_bytes.decode())

                if not cleaned_line or "TERM environment variable not set" in cleaned_line:
                    continue

                try:
                    parsed_json = json.loads(cleaned_line)

                    if isinstance(parsed_json, list) and parsed_json and isinstance(parsed_json[0], str):
                        yield {"type": "error", "message": parsed_json[0]}
                        return

                    yield self._scoped_payload(metric_scope, parsed_json, host)

                except json.JSONDecodeError:
                    if process.returncode or "[ERROR]" in cleaned_line:
                        yield {"type": "error", "message": cleaned_line}
                        return
                    continue

        except Exception as e:
            yield {"type": "error", "message": f"Internal metrics collection error: {str(e)}"}
        finally:
            if process.returncode is None:
                try:
                    process.terminate()
                    await process.wait()
                except Exception:
                    pass

    ## Background fetching services

    def get_collection_status(self, server_ip: str) -> dict:
        return {
            "server_ip": server_ip,
            "collecting": self.job_control.is_running(METRICS_COLLECTION_JOB, server_ip),
        }

    def set_collection_enabled(self, server_ip: str, enabled: bool) -> dict:
        if enabled:
            return self.start_new_metric_collection_job(server_ip)
        return self.stop_metric_collection_job(server_ip)

    def start_new_metric_collection_job(self, server_ip: str) -> dict:
        self._require_configured_host(server_ip)

        if self.job_control.is_running(METRICS_COLLECTION_JOB, server_ip):
            return self.get_collection_status(server_ip)

        task = asyncio.create_task(self._background_fetch_metrics_and_store(server_ip))
        self.job_control.add_job(METRICS_COLLECTION_JOB, server_ip, task)
        return self.get_collection_status(server_ip)

    def stop_metric_collection_job(self, server_ip: str) -> dict:
        task = self.job_control.remove_job(METRICS_COLLECTION_JOB, server_ip)
        if task is not None and not task.done():
            task.cancel()
        return self.get_collection_status(server_ip)

    async def _background_fetch_metrics_and_store(self, server_ip: str) -> None:
        try:
            async for metric in self.stream_server_metrics(MetricScope.ALL, server_ip):
                if metric.get("type") == "error":
                    break

                service_info = metric.get("serviceInfo") or {}
                if not service_info:
                    continue

                save_service_metrics_data(server_ip, service_info)
        except asyncio.CancelledError:
            raise
        finally:
            self.job_control.remove_job(METRICS_COLLECTION_JOB, server_ip)

    def delete_server_metrics(self, server_ip: str) -> dict:
        deleted = delete_metrics_by_ip(server_ip)
        return {"server_ip": server_ip, "deleted": deleted}

    def delete_unused_server_metrics(self) -> dict:
        keep_ips = self._remote_host_ips()
        deleted = delete_unused_metrics(keep_ips)
        return {"deleted": deleted, "kept_servers": keep_ips}

    def delete_all_server_metrics(self) -> dict:
        deleted = delete_all_metrics()
        return {"deleted": deleted}

    # Metrics history fetching services

    def get_service_metrics_history(self, server_ip: str, period: MetricsPeriod) -> dict:
        period_value = period.value
        window_seconds = PERIOD_SECONDS[period_value]
        chunk_seconds = window_seconds // HISTORY_CHUNK_COUNT
        window_start = datetime.now(timezone.utc).timestamp() - window_seconds

        rows = get_service_metrics_averages(
            server_ip,
            start=window_start,
            chunk_seconds=chunk_seconds,
        )

        services = defaultdict(list)
        for service_name, bucket, avg_cpu, avg_memory in rows:
            bucket_time = datetime.fromtimestamp(
                window_start + (bucket * chunk_seconds),
                tz=timezone.utc,
            )
            services[service_name].append(
                {
                    "timestamp": bucket_time.isoformat(),
                    "bucket": bucket,
                    "cpu": round(avg_cpu, 2),
                    "memory": round(avg_memory, 2),
                }
            )

        return {
            "server_ip": server_ip,
            "period": period_value,
            "chunk_seconds": chunk_seconds,
            "chunk_count": HISTORY_CHUNK_COUNT,
            "services": dict(services),
        }
