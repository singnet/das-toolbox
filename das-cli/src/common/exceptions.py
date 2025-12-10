class PortBindingError(Exception):
    """Raised when one or more network ports are already in use."""

    def __init__(self, ports: list[int], host: str = "localhost"):
        self.ports = ports
        self.host = host
        port_label = "Port" if len(ports) == 1 else "Ports"
        ports_str = ", ".join(map(str, ports))
        super().__init__(f"{port_label} {ports_str} on {host} are already in use.")


class InvalidRemoteConfiguration(Exception):
    """Raised when remote configuration is not the same as the local configuration"""

    def __init__(self, *args):
        super().__init__(*args)
