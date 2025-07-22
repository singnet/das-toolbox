from typing import Optional

from common.service_response import ServiceResponse
from common.docker.container_manager import Container

class AttentionBrokerServiceResponse(ServiceResponse):
    def __init__(
        self,
        action: str,
        status: str,
        message: str,
        container: Optional[Container] = None,
        error: Optional[dict] = None,
    ):
        super().__init__(
            service="attention_broker",
            action=action,
            status=status,
            message=message,
            container=container,
            error=error,
        )

