import json
import os
import re
from typing import Optional

from click import ParamType
from click import Path as ClickPath

from common.network import is_server_port_available, is_ssh_server_reachable


class ReachableIpAddress(ParamType):
    name = "reachable ip address"

    def __init__(self, username: str, port: int):
        self.port = port
        self.username = username

    def convert(self, value, param, ctx):

        if not is_server_port_available(
            username=self.username,
            host=value,
            start_port=22,
            end_port=self.port,
        ):
            self.fail(
                "It appears that the port %s on %s is not open."
                % (
                    self.port,
                    value,
                ),
                param,
                ctx,
            )

        if not is_ssh_server_reachable(
            {
                "username": self.username,
                "ip": value,
                "port": self.port,
            }
        ):
            self.fail(
                "%s is not reachable via SSH." % (value),
                param,
                ctx,
            )

        return value

    def __repr__(self):
        return "ReachableIpAddress(%r, %r)" % (self.port, self.username)


class AbsolutePath(ClickPath):
    def __init__(self, *args, **kwargs) -> None:
        if "path_type" not in kwargs:
            kwargs["path_type"] = str

        super().__init__(*args, **kwargs)

    def convert(self, value, param, ctx):
        path = super().convert(value, param, ctx)
        if not os.path.isabs(path):
            self.fail("The path must be absolute.", param, ctx)
        return path


class RegexType(ParamType):
    name = "regex"

    def __init__(self, regex: str, error_message: Optional[str] = None):
        self.regex = re.compile(regex)
        self.error_message = error_message or f"Input does not match regex: {regex}"

    def convert(self, value, param, ctx):
        if not self.regex.match(value):
            self.fail(self.error_message, param, ctx)

        return value


class PortRangeType(ParamType):
    name = "port-range"

    def convert(self, value, param, ctx):
        if not value or ":" not in value:
            self.fail("Invalid port range format. Expected 'start:end'.", param, ctx)

        try:
            start_port, end_port = map(int, value.split(":"))
        except ValueError:
            self.fail("Port range must contain integers like '8000:8100'.", param, ctx)

        if start_port >= end_port:
            self.fail("Invalid port range. Start port must be less than end port.", param, ctx)

        return value


class KeyValueType(ParamType):
    name = "key-value"

    def check_if_nodes_config(self, key: str, val: str) -> bool:
        return "nodes" in key and "root" in val

    def convert_value_to_json(self, value: str) -> dict:
        return json.loads(value)

    def convert(self, value, param, ctx):

        if not value or "=" not in value:
            self.fail("Invalid key-value format. Expected 'key=value'.", param, ctx)

        key, raw_value = value.split("=", 1)
        raw_value = raw_value.strip()
        val = raw_value

        if raw_value.startswith(("{", "[")):
            try:
                val = self.convert_value_to_json(raw_value)
            except json.JSONDecodeError:
                self.fail("Invalid JSON format for value.", param, ctx)

        if self.check_if_nodes_config(key, val):
            self.fail(
                "Using 'root' in node configuration is discouraged. Try setting a different username.",
                param,
                ctx,
            )

        return key, val


class VersionType(ParamType):
    name = "version"

    def convert(self, value, param, ctx):
        if not re.match(r'^\d+\.\d+\.\d+$', value):
            self.fail(
                "Invalid version format. Expected 'X.Y.Z' where X, Y, and Z are integers.",
                param,
                ctx,
            )
        return value


class ValidUsername(ParamType):
    name = "valid-username"

    def __init__(self):
        super().__init__()

    _re = re.compile(r'^[a-z_][a-z0-9_-]{0,31}$')
    _blocked_usernames = {"root"}

    def convert(self, value, param, ctx):

        if not self._re.match(value):
            self.fail(
                "Invalid username. Usernames must start with a letter or underscore, "
                "followed by letters, digits, underscores, or hyphens, and be up to 32 characters long.",
                param,
                ctx,
            )

        if value in self._blocked_usernames:
            self.fail(
                f"Connecting directly via {value} user is discouraged, try setting up a different user.",
                param,
                ctx,
            )

        return value
