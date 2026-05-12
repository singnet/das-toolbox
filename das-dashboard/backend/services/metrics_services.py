import subprocess
import json
import asyncio
import re

from shared.dtos.request.dashboard_get_metrics_dto import GetMetricsDto
from shared.enums.metric_scope import MetricScope
from shared.exceptions.custom_exceptions import DasCliNotInstalledException


class MetricsServices:

    def __init__(self):
        pass

    def run_command(self):

        try:

            results = subprocess.run(
                ["das-cli", "system", "status", "-o", "json"],
                capture_output=True,
                text=True,
                check=True,
            )

            return results.stdout

        except FileNotFoundError:
            raise DasCliNotInstalledException(
                error_message="das-cli executable was not found in PATH."
            )

    def run_command_stream(self):

        try:
            return subprocess.Popen(
                ["das-cli", "system", "status", "--stream", "-o", "json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

        except FileNotFoundError:
            raise DasCliNotInstalledException(
                error_message="das-cli executable was not found in PATH."
            )


    def load_server_metrics(self, requestDTO: GetMetricsDto):

        result = self.run_command()

        return json.loads(result)


    async def define_response_scope(self, metric_scope : MetricScope, parsed : dict):

        match metric_scope:
            case MetricScope.SERVER:
                return {
                    "machineInfo": parsed.get("machineInfo", {})
                }
            
            case MetricScope.SERVICE:
                return {
                    "serviceInfo": parsed.get("serviceInfo", {})
                }
            
            case MetricScope.ALL:
                return parsed
            
            case _:
                return parsed

    async def stream_server_metrics(self, metric_scope : MetricScope):

        process = self.run_command_stream()

        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

        try:
            while True:

                line = await asyncio.to_thread(
                    process.stdout.readline
                )

                if not line:
                    break

                line = ansi_escape.sub('', line).strip() # This clears the first line that comes with ANSI broken chars.
                if not line:
                    continue

                try:
                    json_parsed = json.loads(line)
                    response = await self.define_response_scope(metric_scope, json_parsed)

                    yield response

                except json.JSONDecodeError as e:
                    print("JSON ERROR:", repr(line))
                    print(e)
                    continue
        finally:
            process.kill()