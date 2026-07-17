import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services_init import QUERY_SERVICES
from shared.exceptions.custom_exceptions import CommandRouterConnectionError

router = APIRouter(prefix="/query", tags=["Query", "Query Agent"])

TERMINAL_STATUSES = frozenset({"completed", "error", "aborted"})


class QueryExecutionBody(BaseModel):
    command_type: str
    command_text: str


@router.get("/ping")
def proxy_health_check():
    response = QUERY_SERVICES.health_check_proxy()

    return JSONResponse(
        status_code=response.status_code,
        content=response.text,
    )


@router.post("/executions")
def create_execution_on_proxy(body: QueryExecutionBody):
    response = QUERY_SERVICES.execute_proxy_command(
        body.command_type,
        body.command_text,
    )

    return JSONResponse(
        status_code=response.status_code,
        content=_proxy_json_content(response),
    )


@router.get("/executions/{execution_id}")
def get_execution_status(execution_id: str):
    response = QUERY_SERVICES.get_query_status(execution_id)

    return JSONResponse(
        status_code=response.status_code,
        content=_proxy_json_content(response),
    )


@router.post("/executions/{execution_id}/cancel")
def cancel_query_execution(execution_id: str):
    response = QUERY_SERVICES.cancel_query_execution(execution_id)

    return JSONResponse(
        status_code=response.status_code,
        content=_proxy_json_content(response),
    )


@router.websocket("/executions/{execution_id}")
async def get_execution_stream(websocket: WebSocket, execution_id: str):
    await websocket.accept()

    try:
        async for event in QUERY_SERVICES.stream_execution_events(execution_id):
            await websocket.send_json(event)

            status = event.get("status")
            if status in TERMINAL_STATUSES:
                break
    except WebSocketDisconnect:
        pass
    except CommandRouterConnectionError as error:
        await websocket.send_json(
            {
                "execution_id": execution_id,
                "status": "error",
                "message": error.message,
            }
        )
    except json.JSONDecodeError:
        await websocket.send_json(
            {
                "execution_id": execution_id,
                "status": "error",
                "message": "Invalid JSON received from the command router stream.",
            }
        )


def _proxy_json_content(response):
    try:
        return response.json()
    except ValueError:
        return {"content": response.text}
