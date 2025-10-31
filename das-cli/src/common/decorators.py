import os
from functools import wraps
from typing import Callable, List, Union

from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .command import StdoutSeverity, StdoutType
from .docker.exceptions import DockerContainerNotFoundError
from .settings import Settings


def ensure_container_running(
    cls_backend_attr: Union[List[str], str],
    exception_text: str = "",
    verbose: bool = True,
):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            _load_settings()

            backends = _get_backends(self, cls_backend_attr)
            container_not_running = _check_backends_status(self, backends, verbose)

            if container_not_running:
                raise DockerContainerNotFoundError(exception_text)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator


def _load_settings():
    settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
    settings.raise_on_missing_file()
    settings.raise_on_schema_mismatch()


def _get_backends(self, cls_backend_attr: Union[List[str], str]):
    if isinstance(cls_backend_attr, list):
        return [getattr(self, attr) for attr in cls_backend_attr if hasattr(self, attr)]
    return [getattr(self, cls_backend_attr)]


def _normalize_status(status) -> list[dict]:
    if isinstance(status, dict):
        return [status]
    elif isinstance(status, list):
        return status
    else:
        raise TypeError(f"Unexpected container status type: {type(status)}")


def _check_backends_status(self, backends, verbose: bool) -> bool:
    container_not_running = False

    for backend in backends:
        status_list = _normalize_status(backend.status())

        for container_status in status_list:
            if not _check_container(self, container_status, verbose):
                container_not_running = True

    return container_not_running


def _check_container(self, container_status: dict, verbose: bool) -> bool:
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
                {
                    "service": name,
                    "action": "check",
                    "status": "not_running",
                    "image": image,
                    "port": port,
                },
                stdout_type=StdoutType.MACHINE_READABLE,
            )

    return is_ok
