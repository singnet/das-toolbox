from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services_init import QUERY_SERVICES

router = APIRouter(prefix="/query", tags=["Query", "Query Agent"])

@router.get("/ping")
def proxy_health_check():
    response = QUERY_SERVICES.health_check_proxy()

    return JSONResponse(
        status_code=response.status_code,
        content=response.text
    )


@router.post("/executions")
def create_execution_on_proxy():
    pass

@router.get("/executions/{id}")
def get_execution_status():
    pass

@router.post("/executions/{id}/cancel")
def cancel_query_execution():
    pass

@router.websocket("/executions/{id}")
def get_execution_stream():
    pass