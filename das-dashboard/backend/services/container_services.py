from shared.dtos.request.dashboard_action_dto import DashboardActionDTO
from shared.enums.action_types import ActionTypes;
from shared.exceptions.custom_exceptions import DasCliCommandException, DasCliNotInstalledException

import subprocess

class ContainerServices():

    def _run_subprocess(self, service_name: str, action: str, *extra_args):

        try:
            cmd = ["das-cli", service_name, action, *extra_args]

            results = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            if results.returncode != 0:
                raise DasCliCommandException(
                    error_message="There was an error running this das cli command.",
                    stderror=results.stderr
                )

            return results

        except FileNotFoundError:
            raise DasCliNotInstalledException(
                error_message="das-cli executable was not found in PATH."
            )

    def _mount_remote_args(self, requestDTO: DashboardActionDTO):
        is_remote = requestDTO.targetIp not in [
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
        ]

        if not is_remote:
            return []
        else:
            return [
                "--remote",
                "--host", requestDTO.targetIp,
                "-u", requestDTO.targetUsername,
                "-k", requestDTO.target_ssh_file_path,
            ]



    def start_das_cli_container(self, requestDTO : DashboardActionDTO):

        remote_args = self._mount_remote_args(requestDTO)

        result = self._run_subprocess(
            requestDTO.target_service,
            ActionTypes.START.value,
            *remote_args
        )

        return result

    def stop_das_cli_container(self, requestDTO : DashboardActionDTO):

        remote_args = self._mount_remote_args(requestDTO)

        result = self._run_subprocess(
            requestDTO.target_service,
            ActionTypes.START.value,
            *remote_args
        )

        return result


    def restart_das_cli_container(self, requestDTO : DashboardActionDTO):

        remote_args = self._mount_remote_args(requestDTO)

        result = self._run_subprocess(
            requestDTO.target_service,
            ActionTypes.START.value,
            *remote_args
        )

        return result

