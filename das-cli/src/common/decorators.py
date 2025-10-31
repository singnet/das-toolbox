import os
from functools import wraps
from typing import Callable, List

from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .command import StdoutSeverity, StdoutType
from .docker.exceptions import DockerContainerNotFoundError
from .settings import Settings


def ensure_container_running(
    cls_backend_attr: List[str] | str,
    exception_text: str = "",
    verbose: bool = True,
):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))
            settings.raise_on_missing_file()
            settings.raise_on_schema_mismatch()

            backends = (
                [
                    getattr(self, attr)
                    for attr in cls_backend_attr
                    if hasattr(self, attr)
                ]
                if isinstance(cls_backend_attr, list)
                else [getattr(self, cls_backend_attr)]
            )

            container_not_running = False

            for backend in backends:
                status_list = (
                    backend.status()
                )

                for container_status in status_list:
                    name = container_status.get("container_name")
                    image = container_status.get("image")
                    running = container_status.get("running", False)
                    healthy = container_status.get("healthy", False)
                    port = container_status.get("port", "unknown")
k
                    if not running or not healthy:
                        container_not_running = True
                        if verbose:
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
                    else:
                        if verbose:
                            self.stdout(
                                f"{name} is running on port {port}",
                                severity=StdoutSeverity.WARNING,
                            )

            if container_not_running:
                raise DockerContainerNotFoundError(exception_text)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
