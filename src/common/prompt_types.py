import os
import re
from typing import Union

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

    def __init__(self, username: str, port: Union[int, None] = None):
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
    def __init__(self, *args, **kwargs):
        super().__init__(path_type=str, *args, **kwargs)

    def convert(self, value, param, ctx):
        path = super().convert(value, param, ctx)
        if not os.path.isabs(path):
            self.fail("The path must be absolute.", param, ctx)
        return path
