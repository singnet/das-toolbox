class PortBindingError(Exception):
    """Raised when one or more network ports are already in use."""

    def __init__(self, ports: list[int], host: str = "localhost"):
        self.ports = ports
        self.host = host
        ports_str = ", ".join(map(str, ports))
        super().__init__(f"Ports {ports_str} on {host} are already in use.")

