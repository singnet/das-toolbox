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

            if isinstance(cls_backend_attr, list):
                backends = [
                    getattr(self, attr) if hasattr(self, attr) else None
                    for attr in cls_backend_attr
                ]
            else:
                backends = [getattr(self, cls_backend_attr) if hasattr(self, cls_backend_attr) else None]

            for backend in backends:
                if not backend.is_running():
                    if verbose:
                        self.stdout(
                            "One or more required services are not running.",
                            severity=StdoutSeverity.ERROR,
                        )
                        status = backend.status()
                        for service, is_running in status.items():
                            if not is_running:
                                self.stdout(
                                    {
                                        "service": service,
                                        "action": "check",
                                        "status": "not_running",
                                    },
                                    stdout_type=StdoutType.MACHINE_READABLE,
                                )
                    raise DockerContainerNotFoundError(exception_text)
                else:
                    if verbose:
                        status = backend.status()
                        self.stdout(
                            "All required services are running: ",
                            severity=StdoutSeverity.WARNING,
                        )
                        for service in status.keys():
                            self.stdout(f"- {service}: running")

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
