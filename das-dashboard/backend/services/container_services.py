from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.builders.atom_db_builder import AtomDbBuilder
from shared.enums.action_types import ActionTypes
from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import LOCAL_HOSTS
from shared.utils.das_cli_command import build_host_cli_command
from shared.exceptions.custom_exceptions import (
    ConfigurationValueNotFoundError,
    DasCliCommandException,
)
from shared.utils.das_cli_response import (
    DEFAULT_CLI_ERROR_MESSAGE,
    run_das_cli_json_command,
)
from shared.utils.service_inventory import ORCHESTRATION_ORDER
from shared.utils.path_utils import split_endpoint


class ContainerServices:

    _SKIP_ERROR_MARKERS = ("No such command",)

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def manage_container(
        self,
        action: ActionTypes,
        container_name: str = None,
        command: str = None,
        host: str | None = None,
    ):
        service_command = command or container_name
        if service_command == "db" and (host is None or host in LOCAL_HOSTS):
            config = self.web_config.load_raw_configuration()
            if config.get("atomdb", {}).get("type") == "remotedb":
                return self._manage_remote_atomdb(action, config)
        resolved_host = host or self._resolve_service_host(service_command)
        generated_command = self.build_das_cli_command(
            host=resolved_host,
            service_command=service_command,
            action=action.value,
        )
        return self.run_das_cli_command(generated_command)

    def _manage_remote_atomdb(self, action: ActionTypes, config: dict):
        username = self.web_config.user_profile.get("profile_username") or ""
        hosts = AtomDbBuilder(username).build_remote_peer_configs(config)
        operations = [(host, "db") for host in hosts]
        local_peer = any(
            peer.get("type") == "redismongodb"
            and all(
                split_endpoint(peer.get(database, {}).get("endpoint"), "", 0)[0] in LOCAL_HOSTS
                for database in ("redis", "mongodb")
            )
            for peer in config.get("atomdb", {}).get("remote_peers", [])
        )
        if local_peer:
            operations.append(("localhost", "db"))
        if not operations:
            raise ValueError("RemoteDB requires at least one peer.")
        if action == ActionTypes.STOP:
            operations.reverse()
        results = []
        for host, service in operations:
            command = self.build_das_cli_command(host, service, action.value)
            results.append({"host": host, **self.run_das_cli_command(command)})
        return {"success": True, "results": results}

    def orchestrate_architecture(self, action: ActionTypes, services: list[str]):
        ordered_services = self._order_services(services, action)
        commands_to_run = {}
        has_local_command = False

        for service_command in ordered_services:
            try:
                host = self._resolve_service_host(service_command)
            except ConfigurationValueNotFoundError:
                continue

            if not self._is_remote(host):
                has_local_command = True

            commands_to_run[service_command] = self.build_das_cli_command(
                host=host,
                service_command=service_command,
                action=action.value,
            )

        if not commands_to_run:
            raise ValueError("No valid services to orchestrate.")

        if has_local_command:
            return self._orchestrate_local(commands_to_run)

        return self._orchestrate_remote(commands_to_run)

    def _order_services(self, services: list[str], action: ActionTypes) -> list[str]:
        requested = set(services)
        unknown = requested - set(ORCHESTRATION_ORDER)

        if unknown:
            raise ValueError(f"Unsupported service(s): {', '.join(sorted(unknown))}")

        order = (
            ORCHESTRATION_ORDER
            if action == ActionTypes.START
            else tuple(reversed(ORCHESTRATION_ORDER))
        )
        return [name for name in order if name in requested]

    def _orchestrate_local(self, commands: dict) -> list:
        results = []
        errors = []

        for service_name, cmd in commands.items():
            outcome = self._run_service_command(service_name, cmd)
            if outcome.get("skipped"):
                results.append(outcome)
                continue
            if outcome.get("success"):
                results.append(outcome)
                continue
            errors.append(outcome["error"])

        if errors:
            raise DasCliCommandException(
                message="One or more services failed.",
                detail="\n".join(errors),
            )

        return results

    def _orchestrate_remote(self, commands: dict) -> list:
        results = []
        errors = []

        with ThreadPoolExecutor(max_workers=min(len(commands) or 1, 12)) as executor:
            future_to_service = {
                executor.submit(self._run_service_command, service_name, cmd): service_name
                for service_name, cmd in commands.items()
            }

            for future in as_completed(future_to_service):
                outcome = future.result()
                if outcome.get("skipped") or outcome.get("success"):
                    results.append(outcome)
                    continue
                errors.append(outcome["error"])

        if errors:
            raise DasCliCommandException(
                message="One or more services failed.",
                detail="\n".join(errors),
            )

        return results

    def _run_service_command(self, service_name: str, cmd: list) -> dict:
        try:
            data = self.run_das_cli_command(cmd)
            return {"success": True, "service": service_name, **data}
        except DasCliCommandException as exc:
            detail = str(exc)
            if self._should_skip_error(detail):
                return {
                    "success": True,
                    "skipped": True,
                    "service": service_name,
                    "reason": detail,
                }
            error_message = exc.message or DEFAULT_CLI_ERROR_MESSAGE
            error_detail = exc.detail or detail
            if error_detail and error_detail != error_message:
                error_text = f"Service {service_name} failed: {error_message}\n{error_detail}"
            else:
                error_text = f"Service {service_name} failed: {error_message}"
            return {"success": False, "error": error_text}
        except Exception as exc:
            detail = str(exc) or exc.__class__.__name__
            return {"success": False, "error": f"Service {service_name} failed: {detail}"}

    def _should_skip_error(self, detail: str) -> bool:
        return any(marker in detail for marker in self._SKIP_ERROR_MARKERS)

    def build_das_cli_command(
        self,
        host: str,
        service_command: str,
        action: str,
    ):
        return build_host_cli_command(
            self.web_config, host, [service_command, action, "-o", "json"]
        )

    def run_das_cli_command(self, command: list):
        try:
            stdout_json = run_das_cli_json_command(
                command,
                default_message=DEFAULT_CLI_ERROR_MESSAGE,
            )

            return {
                "success": True,
                "stdout": stdout_json,
                "stderr": "",
                "command": command,
            }

        except DasCliCommandException:
            raise

        except Exception as e:
            raise DasCliCommandException(
                message=DEFAULT_CLI_ERROR_MESSAGE,
                detail=str(e) or e.__class__.__name__,
            )

    def _resolve_service_host(self, service_command: str) -> str:
        service_config = self.web_config.get_service_config(service_command)
        return service_config["host"]

    def _is_remote(self, host: str) -> bool:
        return host not in LOCAL_HOSTS
