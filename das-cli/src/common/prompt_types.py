import os
import re
from typing import Optional

from click import ParamType
from click import Path as ClickPath

from common.network import is_server_port_available


class FunctionVersion(ParamType):
    name = "function version"

    def convert(self, value, param, ctx):
        if value != "latest" and not re.match(r"v?\d+\.\d+\.\d+", value):
            self.fail("The version must follow the format x.x.x (e.g 1.10.9)", param, ctx)

        return value

    def __repr__(self):
        return "FunctionVersion()"


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
        ):
            self.fail("%s is not reachable via SSH." % (value,), param, ctx)

        if not is_server_port_available(
            username=self.username,
            host=value,
            start_port=self.port,
        ):
            self.fail(
                "It appears that the port %s on %s is not open." % (self.port, value),
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
