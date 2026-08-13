from datetime import datetime
from enum import Enum
from typing import Any, Optional

from .docker.container_manager import Container


class StdoutStatus(Enum):
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"


CONTAINER_START_FAILURE_MESSAGE = "DAS-CLI failed to instantiate a container of this service."


class ServiceResponse:
    def __init__(
        self,
        service: str,
        action: str,
        status: StdoutStatus | str,
        message: str | tuple[str],
        container: Optional[Container] = None,
        error: Any = None,
        **extra_details,
    ):
        self.service = service
        self.action = action
        self.status = status
        self.message = " ".join(message) if isinstance(message, tuple) else message
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.container = container
        self.error = error
        self.extra_details = extra_details

    @staticmethod
    def _serialize_status(status: StdoutStatus | str) -> str:
        if isinstance(status, Enum):
            return status.value
        return status

    @staticmethod
    def _serialize_error(error: Any) -> Any:
        if isinstance(error, dict):
            return error
        if isinstance(error, Exception):
            return {"type": type(error).__name__, "message": str(error)}
        return {"message": str(error)}

    def __iter__(self):
        details = {"container": dict(self.container) if self.container else None}
        details.update(self.extra_details)

        yield "service", self.service
        yield "action", self.action
        yield "status", self._serialize_status(self.status)
        yield "message", self.message
        yield "timestamp", self.timestamp
        yield "details", details

        if self.error:
            yield "error", self._serialize_error(self.error)
