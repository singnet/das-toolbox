def split_endpoint(
    endpoint: str,
    default_host: str = "localhost",
    default_port: int = 40020,
) -> tuple[str, int]:
    if not endpoint:
        return default_host, default_port

    value = str(endpoint).strip()

    if value.startswith("["):
        close = value.find("]")
        if close != -1:
            host = value[1:close] or default_host
            port_part = value[close + 1 :]
            if port_part.startswith(":"):
                port_part = port_part[1:]
            return host, int(port_part) if port_part else default_port

    host, separator, port = value.rpartition(":")
    if not separator:
        return value or default_host, default_port

    return host or default_host, int(port) if port else default_port


def replace_endpoint_port(
    endpoint: str,
    new_port: int | str,
    default_host: str = "localhost",
) -> str:
    """Replace only the port, preserving bracketed IPv6 hosts like [::1]:40008."""
    value = str(endpoint or "").strip()
    host, _ = split_endpoint(value, default_host, 0)

    if value.startswith("["):
        return f"[{host}]:{new_port}"

    return f"{host}:{new_port}"
