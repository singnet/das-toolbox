from pydantic import BaseModel

class QueryExecutionDto(BaseModel):
    command_type: str
    command_text: str
