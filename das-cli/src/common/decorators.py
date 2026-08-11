import os
from functools import wraps
from typing import Callable, List, Union

from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .command import StdoutSeverity
from .service_response import ServiceResponse, StdoutStatus
from .docker.exceptions import DockerContainerNotFoundError
from .settings import Settings

LOCAL_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
}


def ensure_container_running(
    cls_backend_attr: Union[List[str], str],
    exception_text: str = "",
    verbose: bool = True,
):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            settings = _load_settings()

            if _is_remote_configuration(settings):
                return func(self, *args, **kwargs)

            backends = _get_backends(self, cls_backend_attr)
            container_not_running = _check_backends_status(
                self,
                backends,
                verbose,
            )

            if container_not_running:
                raise DockerContainerNotFoundError(exception_text)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def _load_settings() -> Settings:
    settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

    settings.validate_configuration_file()

    return settings


def _get_backends(
    self,
    cls_backend_attr: Union[List[str], str],
):
    if isinstance(cls_backend_attr, list):
        return [getattr(self, attr) for attr in cls_backend_attr if hasattr(self, attr)]

    return [getattr(self, cls_backend_attr)]


def _normalize_status(status) -> list[dict]:
    if isinstance(status, dict):
        return [status]

    if isinstance(status, list):
        return status

    raise TypeError(f"Unexpected container status type: {type(status)}")


def _check_backends_status(
    self,
    backends,
    verbose: bool,
) -> bool:

    container_not_running = False

    for backend in backends:
        status_list = _normalize_status(backend.status())

        for container_status in status_list:
            if not _check_container(
                self,
                container_status,
                verbose,
            ):
                container_not_running = True

    return container_not_running


def _check_container(
    self,
    container_status: dict,
    verbose: bool,
) -> bool:

    name = container_status.get("container_name")
    image = container_status.get("image")
    running = container_status.get("running", False)
    healthy = container_status.get("healthy", False)
    port = container_status.get("port", "unknown")

    is_ok = running and healthy

    if verbose:
        if is_ok:
            self.stdout(
                f"{name} is running on port {port}",
                severity=StdoutSeverity.WARNING,
            )

        else:
            self.stdout(
                f"{name} is not running on port {port}",
                severity=StdoutSeverity.ERROR,
            )

            self.stdout(
                ServiceResponse(
                    service=name,
                    action="check",
                    status=StdoutStatus.ERROR,
                    message=f"{name} is not running on port {port}",
                    image=image,
                    port=port,
                ),
                severity=StdoutSeverity.ERROR,
            )

    return is_ok


def _is_remote_configuration(
    settings: Settings,
) -> bool:

    config: dict = settings._store.get_content()

    return _contains_remote_endpoint(config)


def _contains_remote_endpoint(
    value,
) -> bool:

    if isinstance(value, dict):

        endpoint = value.get("endpoint")

        if isinstance(endpoint, str):
            host = endpoint.split(":")[0].strip()

            if host and host not in LOCAL_HOSTS:
                return True

        for child in value.values():
            if _contains_remote_endpoint(child):
                return True

    elif isinstance(value, list):

        for item in value:
            if _contains_remote_endpoint(item):
                return True

    return False
