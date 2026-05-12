from pydantic import BaseModel
from shared.enums.action_types import ActionTypes

class DashboardActionDTO(BaseModel):
    targetIp : str
    targetUsername : str
    targetService : str
    targetAction : ActionTypes


    