import subprocess
import json
import asyncio
import re
from shared.enums.metric_scope import MetricScope
from shared.exceptions.custom_exceptions import DasCliNotInstalledException

class MetricsServices:
    def __init__(self):
        self.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def _get_base_command(self, target_info: dict):
        ip = target_info.get("ip", "127.0.0.1")
        is_local = ip in ["localhost", "127.0.0.1", "0.0.0.0"]
        
        if is_local:
            return ["das-cli"]
        
        cmd = ["das-cli", "--remote", "--host", ip]
        if target_info.get("username"):
            cmd.extend(["-u", target_info["username"]])
        if target_info.get("key_file"):
            cmd.extend(["-k", target_info["key_file"]])
        if target_info.get("port"):
            cmd.extend(["-p", str(target_info["port"])])
            
        return cmd

    def run_command(self, target_info: dict):
        try:
            base_cmd = self._get_base_command(target_info)
            return subprocess.run(
                base_cmd + ["system", "status", "-o", "json"],
                capture_output=True, text=True, check=True,
            )
        except FileNotFoundError:
            raise DasCliNotInstalledException(error_message="das-cli not found.")

    def run_command_stream(self, target_info: dict):
        try:
            base_cmd = self._get_base_command(target_info)
            return subprocess.Popen(
                base_cmd + ["system", "status", "--stream", "-o", "json"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
        except FileNotFoundError:
            raise DasCliNotInstalledException(error_message="das-cli not found.")

    def define_response_scope(self, metric_scope: MetricScope, parsed: dict, target_ip: str):
        parsed["machine"] = {"ip": target_ip}
        if metric_scope == MetricScope.SERVER:
            return {"machineInfo": parsed.get("machineInfo", {}), "machine": parsed["machine"]}
        if metric_scope == MetricScope.SERVICE:
            return {"serviceInfo": parsed.get("serviceInfo", {}), "machine": parsed["machine"]}
        return parsed

    async def load_server_metrics(self, metric_scope: MetricScope, target_info: dict):
        result = self.run_command(target_info)
        return self.define_response_scope(metric_scope, json.loads(result.stdout), target_info.get("ip"))

    async def stream_server_metrics(self, metric_scope: MetricScope, target_info: dict):
        process = self.run_command_stream(target_info)
        try:
            while True:
                line = await asyncio.to_thread(process.stdout.readline)
                if not line: break
                line = self.ansi_escape.sub('', line).strip()
                if not line or not line.startswith('{'): continue
                try:
                    yield self.define_response_scope(metric_scope, json.loads(line), target_info.get("ip"))
                except json.JSONDecodeError: continue
        finally:
            process.terminate()