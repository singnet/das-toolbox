from dtos.dashboard_action_dto import DashboardActionDTO
from enums.action_types import ActionTypes;
import subprocess

class ContainerServices():

    def _run_subprocess(self, service_name : str, action : str, **kwargs):

        results = subprocess.run(['das-cli', service_name, action, *kwargs.values], check=True)

        return results

    def _verify_if_remote(self, requestDTO: DashboardActionDTO):
        is_remote = requestDTO.target_ip not in [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
        ]

        if not is_remote:
            return {}

        return {
            "remote": "--remote",
            "ip_address": requestDTO.target_ip,
            "port": requestDTO.target_port,
            "ssh_path": requestDTO.target_ssh_file_path,
        }



    def start_das_cli_container(self, requestDTO : DashboardActionDTO):

        remote_args = self._verify_if_remote(requestDTO)

        result = self._run_subprocess(requestDTO.target_service, ActionTypes.START.value, **remote_args)

        return result

    def stop_das_cli_container(self, requestDTO : DashboardActionDTO):

        remote_args = self._verify_if_remote(requestDTO)

        result = self._run_subprocess(requestDTO.target_service, ActionTypes.STOP.value, **remote_args)

        return result


    def restart_das_cli_container(self, requestDTO : DashboardActionDTO):

        remote_args = self._verify_if_remote(requestDTO)

        result = self._run_subprocess(requestDTO.target_service, ActionTypes.RESTART.value, **remote_args)

        return result

