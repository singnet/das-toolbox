import json
import logging
import re
import shlex
import subprocess
from typing import Any

from shared.exceptions.custom_exceptions import (
    DasCliCommandException,
    DasCliNotInstalledException,
)

logger = logging.getLogger(__name__)

ANSI_ESCAPE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
UNEXPECTED_EXIT_BLOCK = re.compile(
    r"\[UnexpectedExit\][\s\S]*?(?:Stderr:\s*already printed\s*|Stdout:\s*already printed\s*)",
    re.IGNORECASE,
)
DEFAULT_CLI_ERROR_MESSAGE = "There was an error while running das-cli."
SUCCESS_STATUSES = {"success", "info"}
ERROR_STATUSES = {"error"}


def clean_cli_output(output: str) -> str:
    return ANSI_ESCAPE.sub("", (output or "").strip())


def sanitize_cli_output_for_user(output: str) -> str:
    cleaned = clean_cli_output(output)
    if not cleaned:
        return ""

    trimmed = UNEXPECTED_EXIT_BLOCK.sub("", cleaned).strip()
    kept_lines: list[str] = []
    for line in trimmed.splitlines():
        stripped = line.strip()
        if stripped in {"Stdout: already printed", "Stderr: already printed"}:
            continue
        kept_lines.append(line.rstrip())

    compact: list[str] = []
    previous_blank = False
    for line in kept_lines:
        is_blank = not line.strip()
        if is_blank and previous_blank:
            continue
        compact.append(line)
        previous_blank = is_blank

    return "\n".join(compact).strip()


def parse_das_cli_stdout(stdout: str) -> dict[str, Any]:
    cleaned = clean_cli_output(stdout)
    if not cleaned:
        raise json.JSONDecodeError("Empty das-cli output", "", 0)

    parsers = (
        lambda text: json.loads(text),
        lambda text: json.loads(text.replace("\n", "")),
    )

    for parse in parsers:
        try:
            payload = parse(cleaned)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            continue

    for line in reversed(cleaned.splitlines()):
        candidate = line.strip()
        if not candidate.startswith("{"):
            continue
        try:
            payload = json.loads(candidate)
            if isinstance(payload, dict):
                return payload
        except json.JSONDecodeError:
            continue

    raise json.JSONDecodeError("No JSON payload in das-cli output", cleaned, 0)


def extract_cli_status(payload: dict[str, Any]) -> str | None:
    status = payload.get("status")
    if status is None:
        return None
    return str(status).lower()


def extract_cli_message(payload: dict[str, Any]) -> str:
    message = payload.get("message")
    if message is None:
        return ""
    if isinstance(message, (list, tuple)):
        return " ".join(str(item) for item in message if item)
    return str(message).strip()


def _append_detail_part(parts: list[str], value: Any) -> None:
    if value is None:
        return

    if isinstance(value, list):
        for item in value:
            _append_detail_part(parts, item)
        return

    if isinstance(value, dict):
        nested_message = value.get("message")
        if nested_message:
            parts.append(str(nested_message))
            return
        parts.append(json.dumps(value, ensure_ascii=False))
        return

    text = str(value).strip()
    if text:
        parts.append(text)


def extract_cli_error_detail(payload: dict[str, Any]) -> str:
    parts: list[str] = []

    _append_detail_part(parts, payload.get("errors"))

    error = payload.get("error")
    if isinstance(error, dict):
        _append_detail_part(parts, error.get("message") or error)
    else:
        _append_detail_part(parts, error)

    details = payload.get("details")
    if isinstance(details, dict):
        _append_detail_part(parts, details.get("errors"))
        nested_error = details.get("error")
        if isinstance(nested_error, dict):
            _append_detail_part(parts, nested_error.get("message") or nested_error)
        else:
            _append_detail_part(parts, nested_error)

    deduped: list[str] = []
    for part in parts:
        if part not in deduped:
            deduped.append(part)

    return "\n".join(deduped)


def is_cli_success(payload: dict[str, Any]) -> bool:
    status = extract_cli_status(payload)
    if status is None:
        return True
    if status in ERROR_STATUSES:
        return False
    return status in SUCCESS_STATUSES or status not in ERROR_STATUSES


def raise_cli_error_from_payload(
    payload: dict[str, Any],
    *,
    default_message: str = DEFAULT_CLI_ERROR_MESSAGE,
) -> None:
    message = extract_cli_message(payload) or default_message
    detail = extract_cli_error_detail(payload)
    raise DasCliCommandException(message=message, detail=detail)


def ensure_cli_success(
    payload: dict[str, Any],
    *,
    default_message: str = DEFAULT_CLI_ERROR_MESSAGE,
) -> dict[str, Any]:
    if is_cli_success(payload):
        return payload
    raise_cli_error_from_payload(payload, default_message=default_message)
    return payload


def _format_manual_recovery_detail(
    *,
    exit_code: int | None,
    cmd: list[str] | None = None,
    stdout: str = "",
    stderr: str = "",
    raw_output: str = "",
) -> str:
    lines: list[str] = []

    if exit_code is not None:
        lines.append(
            f"das-cli exited with status {exit_code} without a formatted JSON response."
        )
    else:
        lines.append("das-cli returned output without a formatted JSON response.")

    if cmd:
        lines.append(f"Command: {' '.join(shlex.quote(part) for part in cmd)}")

    lines.append(
        "Check the server logs or run the command manually in a terminal for details."
    )

    cli_output = sanitize_cli_output_for_user(raw_output or stderr or stdout)
    if cli_output:
        lines.extend(["", "CLI output:", cli_output])
    elif exit_code is not None:
        lines.extend(["", "CLI output: (empty)"])

    return "\n".join(lines)


def raise_cli_command_failure(
    *,
    cmd: list[str],
    exit_code: int,
    stdout: str,
    stderr: str,
    default_message: str = DEFAULT_CLI_ERROR_MESSAGE,
) -> None:
    output = stderr or stdout
    cleaned = clean_cli_output(output)

    if cleaned:
        try:
            payload = parse_das_cli_stdout(cleaned)
        except json.JSONDecodeError:
            logger.error(
                "das-cli failed without JSON: exit=%s cmd=%s stderr=%r stdout=%r",
                exit_code,
                cmd,
                stderr[:500],
                stdout[:500],
            )
            raise DasCliCommandException(
                message=default_message,
                detail=_format_manual_recovery_detail(
                    exit_code=exit_code,
                    cmd=cmd,
                    stdout=stdout,
                    stderr=stderr,
                    raw_output=cleaned,
                ),
            ) from None

        if not is_cli_success(payload):
            raise_cli_error_from_payload(payload, default_message=default_message)

        message = extract_cli_message(payload) or default_message
        raise DasCliCommandException(
            message=message,
            detail=sanitize_cli_output_for_user(cleaned) or cleaned,
        )

    logger.error(
        "das-cli failed without output: exit=%s cmd=%s stderr=%r stdout=%r",
        exit_code,
        cmd,
        stderr[:500],
        stdout[:500],
    )
    raise DasCliCommandException(
        message=default_message,
        detail=_format_manual_recovery_detail(
            exit_code=exit_code,
            cmd=cmd,
            stdout=stdout,
            stderr=stderr,
        ),
    )


def raise_from_cli_output(
    output: str,
    *,
    default_message: str = DEFAULT_CLI_ERROR_MESSAGE,
    exit_code: int | None = None,
    cmd: list[str] | None = None,
    stdout: str = "",
    stderr: str = "",
) -> None:
    cleaned = clean_cli_output(output)
    if not cleaned:
        raise DasCliCommandException(
            message=default_message,
            detail=_format_manual_recovery_detail(
                exit_code=exit_code,
                cmd=cmd,
                stdout=stdout,
                stderr=stderr,
            ),
        )

    try:
        payload = parse_das_cli_stdout(cleaned)
    except json.JSONDecodeError:
        raise DasCliCommandException(
            message=default_message,
            detail=_format_manual_recovery_detail(
                exit_code=exit_code,
                cmd=cmd,
                stdout=stdout or output,
                stderr=stderr,
                raw_output=cleaned,
            ),
        ) from None

    if not is_cli_success(payload):
        raise_cli_error_from_payload(payload, default_message=default_message)

    message = extract_cli_message(payload) or default_message
    raise DasCliCommandException(
        message=message,
        detail=sanitize_cli_output_for_user(cleaned) or cleaned,
    )


def parse_and_validate_cli_stdout(
    stdout: str,
    *,
    default_message: str = DEFAULT_CLI_ERROR_MESSAGE,
) -> dict[str, Any]:
    payload = parse_das_cli_stdout(stdout)
    return ensure_cli_success(payload, default_message=default_message)


def run_das_cli_json_command(
    cmd: list[str],
    *,
    default_message: str = DEFAULT_CLI_ERROR_MESSAGE,
    timeout: float | None = None,
) -> dict[str, Any]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise DasCliCommandException(
            message=default_message,
            detail="The das-cli command timed out.",
        ) from error
    except FileNotFoundError as error:
        raise DasCliNotInstalledException("das-cli not found.") from error

    stdout = result.stdout or ""
    stderr = result.stderr or ""

    if result.returncode != 0:
        raise_cli_command_failure(
            cmd=cmd,
            exit_code=result.returncode,
            stdout=stdout,
            stderr=stderr,
            default_message=default_message,
        )

    try:
        return parse_and_validate_cli_stdout(stdout, default_message=default_message)
    except json.JSONDecodeError:
        logger.warning(
            "das-cli exited 0 but returned no parseable JSON: cmd=%s stdout=%r",
            cmd,
            clean_cli_output(stdout)[:500],
        )
        return {}
