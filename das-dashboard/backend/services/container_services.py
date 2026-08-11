import subprocess
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.enums.action_types import ActionTypes
from shared.internal.web_configuration import WebConfiguration
from shared.internal.constants import DEFAULT_SSHKEY_CLONE_PATH, LOCAL_HOSTS
from shared.exceptions.custom_exceptions import (
    ConfigurationValueNotFoundError,
    DasCliCommandException,
    DASCLIResponseDecodeError,
)
from shared.utils.service_inventory import ORCHESTRATION_ORDER


class ContainerServices:

    _SKIP_ERROR_MARKERS = ("No such command",)
    _ANSI_ESCAPE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    def __init__(self, web_config: WebConfiguration):
        self.web_config = web_config

    def manage_container(
        self,
        action: ActionTypes,
        container_name: str = None,
        command: str = None,
    ):
        service_command = command or container_name
        host = self._resolve_service_host(service_command)
        generated_command = self.build_das_cli_command(
            host=host,
            service_command=service_command,
            action=action.value,
        )
        return self.run_das_cli_command(generated_command)

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
            raise DasCliCommandException(" | ".join(errors))

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
            raise DasCliCommandException(" | ".join(errors))

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
            return {"success": False, "error": f"Service {service_name} failed: {detail}"}
        except DASCLIResponseDecodeError as exc:
            return {"success": False, "error": f"Service {service_name} failed: {exc}"}
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
        cmd = ["das-cli", service_command, action]

        if self._is_remote(host):
            profile = self.web_config.user_profile
            ssh_key = profile.get("profile_ssh_keypath") or DEFAULT_SSHKEY_CLONE_PATH
            cmd.extend([
                "--remote",
                "--host", host,
                "-u", profile.get("profile_username", "root"),
                "-k", ssh_key,
            ])

        cmd.extend(["-o", "json"])
        return cmd

    def run_das_cli_command(self, command: list):
        result = None
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
            )

            stdout_json = self._parse_das_cli_stdout(result.stdout)

            return {
                "success": True,
                "stdout": stdout_json,
                "stderr": result.stderr,
                "command": command,
            }

        except subprocess.CalledProcessError as e:
            error_output = self._clean_cli_output(e.stderr or e.stdout or "Unknown Subprocess Error")
            raise DasCliCommandException(error_output)

        except json.JSONDecodeError as e:
            output = self._clean_cli_output(result.stdout if result else "")
            if result is not None and not output:
                return {
                    "success": True,
                    "stdout": None,
                    "stderr": result.stderr,
                    "command": command,
                }

            raise DasCliCommandException(
                f"Could not parse das-cli output as JSON: {output or '(empty)'}"
            ) from e

        except DasCliCommandException:
            raise

        except Exception as e:
            details = str(e) or e.__class__.__name__

            raise DasCliCommandException(details)

    def _parse_das_cli_stdout(self, stdout: str):
        cleaned = self._ANSI_ESCAPE.sub("", stdout.strip())
        if not cleaned:
            raise json.JSONDecodeError("Empty das-cli output", "", 0)

        parsers = (
            lambda text: json.loads(text),
            lambda text: json.loads(text.replace("\n", "")),
        )

        for parse in parsers:
            try:
                return parse(cleaned)
            except json.JSONDecodeError:
                continue

        for line in reversed(cleaned.splitlines()):
            candidate = line.strip()
            if not candidate.startswith(("{", "[")):
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

        raise json.JSONDecodeError("No JSON payload in das-cli output", cleaned, 0)

    def _clean_cli_output(self, output: str) -> str:
        return self._ANSI_ESCAPE.sub("", output.strip())

    def _resolve_service_host(self, service_command: str) -> str:
        service_config = self.web_config.get_service_config(service_command)
        return service_config["host"]

    def _is_remote(self, host: str) -> bool:
        return host not in LOCAL_HOSTS
