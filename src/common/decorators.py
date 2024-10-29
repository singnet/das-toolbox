from functools import wraps
from typing import List, Callable

from .docker.container_manager import ContainerManager
from .docker.exceptions import DockerContainerNotFoundError

from .command import Command, StdoutSeverity


def ensure_container_running(
    container_manager_list: List[ContainerManager],
    exception_text: str = "",
):
    def decorator(func: Callable):
        @wraps
        def wrapper(*arg, **args):
            container_not_running = False

            for container_manager in container_manager_list:
                service_name = container_manager.get_container().get_name()
                service_port = container_manager.get_port()

                if not container_manager.is_running():
                    Command.stdout(
                        f"{service_name} is not running",
                        severity=StdoutSeverity.ERROR,
                    )
                    container_not_running = True
                else:
                    Command.stdout(
                        f"{service_name} is running on port {service_port}",
                        severity=StdoutSeverity.WARNING,
                    )

            if container_not_running:
                raise DockerContainerNotFoundError(exception_text)

            return func(*arg, **args)

        return wrapper

    return decorator
