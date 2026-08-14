from typing import Any

from pydantic import BaseModel

class QueryExecutionDto(BaseModel):
    command_type: str
    command_text: str
    parameters: dict[str, Any] | None = None
