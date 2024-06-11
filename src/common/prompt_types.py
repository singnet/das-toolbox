import re
from click import IntRange, ParamType, Choice, Path
from common.network import is_server_port_available


class FunctionVersion(ParamType):
    name = "function version"

    def convert(self, value, param, ctx):
        if value != "latest" and not re.match(r"v?\d+\.\d+\.\d+", value):
            self.fail(
                "The version must follow the format x.x.x (e.g 1.10.9)", param, ctx
            )

        return value

    def __repr__(self):
        return "ReachableIpAddress(%r, %r)" % (self.port)


class ReachableIpAddress(ParamType):
    name = "reachable ip address"

    def __init__(self, port=None):
        self.port = port

    def convert(self, value, param, ctx):
        if not is_server_port_available(host=value, start_port=22):
            self.fail("%s is not reachable via SSH." % (value,), param, ctx)

        if not is_server_port_available(host=value, start_port=self.port):
            self.fail(
                "It appears that the Redis port %s on %s is not open."
                % (self.port, value),
                param,
                ctx,
            )

        return value

    def __repr__(self):
        return "ReachableIpAddress(%r, %r)" % (self.port)
