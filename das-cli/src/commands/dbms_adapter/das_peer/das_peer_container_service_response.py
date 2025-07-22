from typing import Optional

from common.service_response import ServiceResponse
from common.docker.container_manager import Container

class DasPeerContainerServiceResponse(ServiceResponse):
    def __init__(
        self,
        action: str,
        status: str,
        message: str,
        container: Optional[Container] = None,
        extra_details: Optional[dict] = None,
        error: Optional[dict] = None,
    ):
        super().__init__(
            service="das_peer",
            action=action,
            status=status,
            message=message,
            container=container,
            error=error,
            **(extra_details or {}),
        )

