from typing import Any

from pydantic import BaseModel, Field


class QueryExecutionDto(BaseModel):
    query_text: str = Field(min_length=1)
    parameters: dict[str, Any] | None = None
