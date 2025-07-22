import os
from functools import wraps
from typing import Callable, List

from common.config.store import JsonConfigStore
from settings.config import SECRETS_PATH

from .command import StdoutType, StdoutSeverity
from .docker.exceptions import DockerContainerNotFoundError
from .settings import Settings


def ensure_container_running(
    cls_container_manager_attrs: List[str],
    exception_text: str = "",
    verbose: bool = True,
):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            settings = Settings(store=JsonConfigStore(os.path.expanduser(SECRETS_PATH)))

            settings.raise_on_missing_file()
            settings.raise_on_schema_mismatch()

            container_not_running = False

            for container_manager_attr in cls_container_manager_attrs:
                if not hasattr(self, container_manager_attr):
                    raise ValueError(
                        f"`{container_manager_attr}` is not a valid container manager attribute."
                    )

                container = getattr(self, container_manager_attr)

                container_instance = container.get_container()
                service_name = container_instance.name
                service_port = container_instance.port

                if not container.is_running():
                    if verbose:
                        self.stdout(
                            f"{service_name} is not running",
                            severity=StdoutSeverity.ERROR,
                        )
                        self.stdout(
                            {
                                "service": service_name,
                                "action": "check",
                                "status": "not_running",
                                "port": service_port,
                            },
                            stdout_type=StdoutType.MACHINE_READABLE,
                        )
                    container_not_running = True
                else:
                    if verbose:
                        self.stdout(
                            f"{service_name} is running on port {service_port}",
                            severity=StdoutSeverity.WARNING,
                        )

            if container_not_running:
                raise DockerContainerNotFoundError(exception_text)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
