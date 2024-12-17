from functools import wraps
from typing import Callable, List

from .command import Command, StdoutSeverity
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
            settings = Settings()

            settings.raise_on_missing_file()

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
                        Command.stdout(
                            f"{service_name} is not running",
                            severity=StdoutSeverity.ERROR,
                        )
                    container_not_running = True
                else:
                    if verbose:
                        Command.stdout(
                            f"{service_name} is running on port {service_port}",
                            severity=StdoutSeverity.WARNING,
                        )

            if container_not_running:
                raise DockerContainerNotFoundError(exception_text)

            return func(self, *args, **kwargs)

        return wrapper

    return decorator
