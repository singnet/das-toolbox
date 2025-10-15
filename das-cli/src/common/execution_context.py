import json
from typing import Optional, Dict
from common.utils import get_server_username
from common.network import get_public_ip


class ExecutionContext:
  def __init__(
    self,
    remote_host: Optional[str] = None,
    remote_port: Optional[int] = 22,
    remote_user: Optional[str] = None,
    remote_password: Optional[str] = None,
    remote_key_path: Optional[str] = None,
    remote_connection_timeout: int = 10,
    context_str: Optional[str] = None,
  ):
    self.connection = {
      "remote_host": remote_host,
      "remote_port": remote_port,
      "remote_user": remote_user,
      "remote_password": remote_password,
      "remote_key_path": remote_key_path,
      "remote_connection_timeout": remote_connection_timeout,
      "client_ip": get_public_ip(),
      "client_username": get_server_username(),
    }

    self.context = self._parse_context(context_str)

  def _parse_context(self, context_str: Optional[str]) -> Dict:
    if not context_str:
      return {}
    try:
      data = json.loads(context_str)
      if not isinstance(data, dict):
        raise ValueError("Context must be a JSON object.")
      return data
    except json.JSONDecodeError as e:
      raise ValueError(f"Invalid JSON passed to --context: {e}")

  def to_dict(self) -> Dict:
    return {
      "connection": self.connection,
      "context": self.context,
    }

  def is_remote(self) -> bool:
    return bool(self.connection["remote_host"])
