import asyncio
import json
import re
import subprocess

from shared.enums.metric_scope import MetricScope
from shared.exceptions.custom_exceptions import DasCliNotInstalledException
from shared.internal.web_configuration import WebConfiguration


LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


class MetricsServices:

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config
        self.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def _is_remote(self, host: str) -> bool:
        return host not in LOCAL_HOSTS

    def _build_remote_flags(self, host: str):
        if not self._is_remote(host):
            return []

        profile = self.web_config.user_profile

        return [
            "--remote",
            "--host", host,
            "-u", profile.get("profile_username", "root"),
            "-k", profile.get("profile_ssh_keypath"),
        ]

    def _build_command(self, host: str, stream: bool = False):

        cmd = ["das-cli", "system", "status"]
        cmd.extend(self._build_remote_flags(host))

        if stream:
            cmd.append("--stream")

        cmd.extend(["-o", "json"])

        return cmd

    def _run_once(self, host: str):

        try:
            return subprocess.run(
                self._build_command(host),
                capture_output=True,
                text=True,
                check=True,
            )

        except FileNotFoundError:
            raise DasCliNotInstalledException(error_message="das-cli not found.")

    def _run_stream(self, host: str):

        try:
            return subprocess.Popen(
                self._build_command(host, stream=True),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

        except FileNotFoundError:
            raise DasCliNotInstalledException(error_message="das-cli not found.")

    def _define_response_scope(self, metric_scope: MetricScope, parsed: dict, host: str):
        server_json = parsed[0] if isinstance(parsed, list) and parsed else parsed

        if metric_scope == MetricScope.SERVER:
            return [{"ip": host, "machineInfo": server_json.get("machineInfo", {})}]

        if metric_scope == MetricScope.SERVICE:
            return [{"ip": host, "serviceInfo": server_json.get("serviceInfo", {})}]

        return [{"ip": host, **server_json}]

    async def load_server_metrics(self, metric_scope: MetricScope, host: str):
        result = self._run_once(host)

        return self._define_response_scope(
            metric_scope,
            json.loads(result.stdout),
            host,
        )

    async def stream_server_metrics(self, metric_scope: MetricScope, host: str):
        process = self._run_stream(host)

        try:
            while True:

                line = await asyncio.to_thread(process.stdout.readline)
                if not line:
                    break

                line = self.ansi_escape.sub("", line).strip()
                if not line or not line.startswith("{"):
                    continue

                try:
                    yield self._define_response_scope(metric_scope, json.loads(line), host)

                except json.JSONDecodeError:
                    continue
        finally:
            process.terminate()