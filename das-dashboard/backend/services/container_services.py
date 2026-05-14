import subprocess
from shared.exceptions.custom_exceptions import DasCliCommandException, DasCliNotInstalledException

class ContainerServices:
    def _mount_remote_args(self, target_info: dict):
        ip = target_info.get("ip", "127.0.0.1")
        if ip in ["localhost", "127.0.0.1", "0.0.0.0"]:
            return []
        
        args = ["--remote", "--host", ip]
        if target_info.get("username"):
            args.extend(["-u", target_info["username"]])
        if target_info.get("key_file"):
            args.extend(["-k", target_info["key_file"]])
        return args

    def _run_subprocess(self, service_name: str, action: str, target_info: dict, *extra_args):
        try:
            remote_args = self._mount_remote_args(target_info)
            cmd = ["das-cli"] + remote_args + [service_name, action, *extra_args]
            return subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            raise DasCliCommandException(error_message=f"CLI Error: {service_name} {action}", stderror=e.stderr)
        except FileNotFoundError:
            raise DasCliNotInstalledException(error_message="das-cli not found in PATH.")

    def manage_container(self, service_name: str, action: str, target_info: dict):
        return self._run_subprocess(service_name, action, target_info)