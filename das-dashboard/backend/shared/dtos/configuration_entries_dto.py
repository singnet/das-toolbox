from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional


class ConfigurationEntriesDto(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    atomdb: Optional[Dict[str, Any]] = None
    agents_query: Optional[Dict[str, Any]] = Field(default=None, alias="agents.query")
    agents_link_creation: Optional[Dict[str, Any]] = Field(default=None, alias="agents.link_creation")
    agents_evolution: Optional[Dict[str, Any]] = Field(default=None, alias="agents.evolution")
    agents_command_router: Optional[Dict[str, Any]] = Field(default=None, alias="agents.command_router")
    agents_attention: Optional[Dict[str, Any]] = Field(default=None, alias="agents.attention")
    agents_context: Optional[Dict[str, Any]] = Field(default=None, alias="agents.context")
    agents_atomdb: Optional[Dict[str, Any]] = Field(default=None, alias="agents.atomdb")
    agents_basequery: Optional[Dict[str, Any]] = Field(default=None, alias="agents.base_query")
    environment: Optional[Dict[str, Any]] = Field(default=None, alias="environment")
