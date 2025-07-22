from typing import Optional

from common.docker.container_manager import Container
from common.service_response import ServiceResponse


class DbServiceResponse(ServiceResponse):
    def __init__(
        self,
        action: str,
        status: str,
        message: str | tuple[str],
        extra_details: Optional[dict] = None,
        container: Optional[Container] = None,
        error: Optional[dict] = None,
    ):
        super().__init__(
            service="database",
            action=action,
            status=status,
            message=message,
            container=container,
            error=error,
            **(extra_details or {}),
        )
