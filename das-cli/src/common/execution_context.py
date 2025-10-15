from __future__ import annotations

import base64
import json
from datetime import datetime
from typing import Any, Dict, Optional, TypedDict, cast

from common.network import get_public_ip
from common.utils import get_platform_info, get_server_username
from settings.config import VERSION as DAS_CLI_VERSION


class SSHParams(TypedDict, total=False):
    host: str
    port: int
    user: str
    password: str
    key_path: str
    connection_timeout: int


class ExecutionContext:
    """
    Represents the execution environment of a DAS CLI command,
    including platform info, CLI version, invoker metadata, and optional SSH configuration.
    """

    def __init__(self, command_path: str, ssh_params: Optional[SSHParams] = None) -> None:
        self.command_path: str = command_path

        self.source: Dict[str, Any] = {
            "das_cli_version": DAS_CLI_VERSION,
            "platform": get_platform_info(),
            "ssh_params": ssh_params or {},
            "ip": ssh_params.get("host") if ssh_params else None,
            "username": ssh_params.get("user") if ssh_params else None,
        }

        self.invoker: Dict[str, Any] = {
            "ip": get_public_ip(),
            "username": get_server_username(),
        }

        self.created_at: str = datetime.utcnow().isoformat()

    def to_dict(self, include_ssh: bool = False) -> Dict[str, Any]:
        """Return a dictionary representation of the context."""
        data: Dict[str, Any] = {
            "command_path": self.command_path,
            "source": {
                "das_cli_version": self.source.get("das_cli_version"),
                "platform": self.source.get("platform"),
                "ip": self.source.get("ip"),
                "username": self.source.get("username"),
            },
            "invoker": self.invoker,
            "created_at": self.created_at,
        }

        if include_ssh and self.source.get("ssh_params"):
            source_dict = cast(Dict[str, Any], data["source"])
            source_dict["ssh_params"] = self.source["ssh_params"]
            data["source"] = source_dict

        return data

    def to_str(self, include_ssh: bool = False, encode_base64: bool = True) -> str:
        """
        Serialize the context to a JSON (optionally base64-encoded) string.
        Safe to pass via CLI when include_ssh=False.
        """
        json_data = json.dumps(self.to_dict(include_ssh=include_ssh), separators=(",", ":"))
        if encode_base64:
            return base64.urlsafe_b64encode(json_data.encode("utf-8")).decode("utf-8")
        return json_data

    @classmethod
    def from_str(cls, data: str, is_base64: bool = True) -> "ExecutionContext":
        """
        Reconstruct an ExecutionContext from a serialized string.
        ssh_params will be empty unless explicitly included during serialization.
        """
        try:
            json_data = (
                base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8")
                if is_base64
                else data
            )
            obj = json.loads(json_data)
        except Exception as e:
            raise ValueError(f"Invalid context data: {e}")

        instance = cls(command_path=obj.get("command_path", ""))
        instance.source = obj.get("source", {})
        instance.invoker = obj.get("invoker", {})
        instance.created_at = obj.get("created_at", datetime.utcnow().isoformat())
        return instance

    def is_remote(self) -> bool:
        ssh_params = self.source.get("ssh_params", {})
        return bool(ssh_params.get("host"))
