def split_endpoint(endpoint: str, default_host: str = "localhost", default_port: int = 40020) -> tuple[str, int]:
    if not endpoint:
        return default_host, default_port

    host, _, port = str(endpoint).partition(":")
    return host or default_host, int(port) if port else default_port
