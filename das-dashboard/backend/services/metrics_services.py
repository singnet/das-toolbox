import subprocess
import json
import asyncio
import re
from shared.enums.metric_scope import MetricScope
from shared.exceptions.custom_exceptions import DasCliNotInstalledException

class MetricsServices:
    def __init__(self):
        self.ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

    def _build_full_command(self, target_info: dict, sub_commands: list, extra_flags: list = None):
        ip = target_info.get("ip", "127.0.0.1")
        is_local = ip in ["localhost", "127.0.0.1", "0.0.0.0"]
        
        cmd = ["das-cli"] + sub_commands
        
        if not is_local:
            cmd.extend(["--remote", "--host", ip])
            if target_info.get("username"):
                cmd.extend(["-u", target_info["username"]])
            if target_info.get("key_file"):
                cmd.extend(["-k", target_info["key_file"]])
            if target_info.get("port"):
                cmd.extend(["-p", str(target_info["port"])])
        
        if extra_flags:
            cmd.extend(extra_flags)
            
        return cmd

    def run_command(self, target_info: dict):
        try:
            full_cmd = self._build_full_command(
                target_info, 
                ["system", "status"], 
                ["-o", "json"]
            )
            return subprocess.run(
                full_cmd,
                capture_output=True, text=True, check=True,
            )
        except FileNotFoundError:
            raise DasCliNotInstalledException(error_message="das-cli not found.")

    def run_command_stream(self, target_info: dict):
        try:
            full_cmd = self._build_full_command(
                target_info, 
                ["system", "status"], 
                ["--stream", "-o", "json"]
            )
            return subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
        except FileNotFoundError:
            raise DasCliNotInstalledException(error_message="das-cli not found.")

    def define_response_scope(self, metric_scope: MetricScope, parsed: dict, target_ip: str):

        if isinstance(parsed, list) and len(parsed) > 0:
            server_json = parsed[0]
        else:
            server_json = parsed

        if metric_scope == MetricScope.SERVER:
            return [{"ip": target_ip , "machineInfo": server_json.get("machineInfo", {})}]
        if metric_scope == MetricScope.SERVICE:
            return [{"ip": target_ip, "serviceInfo": server_json.get("serviceInfo", {})}]
        
        return [{"ip": target_ip, **server_json}]

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