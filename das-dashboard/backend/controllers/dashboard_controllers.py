from fastapi import APIRouter
from fastapi.responses import JSONResponse

from services_init import DASHBOARD_SERVICES

router = APIRouter(tags=["Dashboard"])


@router.get("/initial-state")
async def get_initial_state():
    content = await DASHBOARD_SERVICES.fetch_initial_state()

    return JSONResponse(status_code=200, content=content)
