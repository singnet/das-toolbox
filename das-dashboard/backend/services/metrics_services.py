import asyncio
import json
import re

from shared.enums.metric_scope import MetricScope
from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH, LOCAL_HOSTS
from shared.exceptions.custom_exceptions import (
    DasCliNotInstalledException,
    DasCliCommandException
)


class MetricsServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config
        self.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def _is_remote(self, host: str) -> bool:
        return host not in LOCAL_HOSTS

    def _build_remote_flags(self, host: str) -> list:
        if not self._is_remote(host):
            return []

        profile = self.web_config.user_profile
        ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH

        return [
            "--remote",
            "--host", host,
            "-u", profile.get("profile_username", "root"),
            "-k", ssh_key,
        ]

    def _build_command(self, host: str, stream: bool = False) -> list:
        cmd = ["das-cli", "system", "status"]
        cmd.extend(self._build_remote_flags(host))

        if stream:
            cmd.append("--stream")

        cmd.extend(["-o", "json"])
        return cmd

    async def _run_async_process(self, host: str, stream: bool = False):
        try:
            return await asyncio.create_subprocess_exec(
                *self._build_command(host, stream=stream),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except FileNotFoundError:
            raise DasCliNotInstalledException("das-cli not found.")

    def _define_response_scope(self, metric_scope: MetricScope, parsed: dict, host: str) -> dict:
        server_json = parsed[0] if isinstance(parsed, list) and parsed else parsed

        if not isinstance(server_json, dict):
            return {"ip": host, "type": "error", "message": str(server_json)}

        if metric_scope == MetricScope.SERVER:
            return {"ip": host, "machineInfo": server_json.get("machineInfo", {})}

        if metric_scope == MetricScope.SERVICE:
            return {"ip": host, "serviceInfo": server_json.get("serviceInfo", {})}

        return {"ip": host, **server_json}

    async def load_server_metrics(self, metric_scope: MetricScope, host: str):
        process = await self._run_async_process(host, stream=False)
        stdout, _ = await process.communicate()
        stdout_str = stdout.decode().strip()
        cleaned_stdout = self.ansi_escape.sub("", stdout_str)

        if process.returncode and process.returncode != 0:
            try:
                parsed_err = json.loads(cleaned_stdout)
                if isinstance(parsed_err, list) and parsed_err:
                    cleaned_stdout = parsed_err[0]
            except Exception:
                pass
            raise DasCliCommandException(cleaned_stdout or "Unknown Remote Connection Error")

        try:
            parsed_json = json.loads(cleaned_stdout)
            if isinstance(parsed_json, list) and parsed_json and isinstance(parsed_json[0], str):
                raise DasCliCommandException(parsed_json[0])
        except json.JSONDecodeError:
            if "\n" in cleaned_stdout:
                cleaned_stdout = cleaned_stdout.split("\n")[-1]
            parsed_json = json.loads(cleaned_stdout)

        return self._define_response_scope(metric_scope, parsed_json, host)

    async def stream_server_metrics(self, metric_scope: MetricScope, host: str):
        process = await self._run_async_process(host, stream=True)

        try:
            async for line_bytes in process.stdout:
                line = line_bytes.decode().strip()
                cleaned_line = self.ansi_escape.sub("", line)

                if not cleaned_line or "TERM environment variable not set" in cleaned_line:
                    continue

                try:
                    parsed_json = json.loads(cleaned_line)
                    
                    if isinstance(parsed_json, list) and parsed_json and isinstance(parsed_json[0], str):
                        yield {"type": "error", "message": parsed_json[0]}
                        return

                    yield self._define_response_scope(metric_scope, parsed_json, host)

                except json.JSONDecodeError:
                    if (process.returncode and process.returncode != 0) or "[ERROR]" in cleaned_line:
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