from datetime import datetime
from typing import Optional
from .docker.container_manager import Container

class ServiceResponse:
    def __init__(
        self,
        service: str,
        action: str,
        status: str,
        message: str,
        container: Optional[Container] = None,
        error: Optional[dict] = None,
        **extra_details,
    ):
        self.service = service
        self.action = action
        self.status = status
        self.message = message
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.container = container
        self.error = error
        self.extra_details = extra_details

    def __iter__(self):
        details = {"container": dict(self.container) if self.container else None}
        details.update(self.extra_details)

        yield "service", self.service
        yield "action", self.action
        yield "status", self.status
        yield "message", self.message
        yield "timestamp", self.timestamp
        yield "details", details

        if self.error:
            yield "error", self.error
