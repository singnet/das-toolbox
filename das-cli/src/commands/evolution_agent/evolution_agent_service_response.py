from typing import Optional

from common.docker.container_manager import Container
from common.service_response import ServiceResponse


class EvolutionAgentServiceResponse(ServiceResponse):
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
            service="evolution_agent",
            action=action,
            status=status,
            message=message,
            container=container,
            error=error,
            **(extra_details or {}),
        )
