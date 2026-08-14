import json
from contextlib import aclosing
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from requests import Response

from services_init import QUERY_SERVICES
from shared.exceptions.custom_exceptions import CommandRouterConnectionError

from shared.dtos.query_execution_dto import QueryExecutionDto

router = APIRouter(prefix="/query", tags=["Query", "Query Agent"])

TERMINAL_STATUSES = frozenset({"completed", "error", "aborted"})


@router.get("/param/defaults")
def get_param_defaults():
    return JSONResponse(
        status_code=200,
        content=QUERY_SERVICES.get_default_params_from_config(),
    )


@router.get("/ping")
def proxy_health_check():
    response = QUERY_SERVICES.health_check_proxy()

    return JSONResponse(
        status_code=response.status_code,
        content=_proxy_json_content(response),
    )


@router.post("/executions")
def create_execution_on_proxy(body: QueryExecutionDto):
    response = QUERY_SERVICES.execute_proxy_command(
        body.command_type,
        body.command_text,
        body.parameters,
    )

    return JSONResponse(
        status_code=response.status_code,
        content=_proxy_json_content(response),
    )


@router.get("/executions/{execution_id}")
def get_execution_status(execution_id: str):
    response = QUERY_SERVICES.get_query_status(execution_id)
    content = _proxy_json_content(response)
    
    return JSONResponse(
        status_code=response.status_code,
        content=content,
    )


@router.get("/executions/{execution_id}/answers")
def get_execution_answers(
    execution_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
):
    return JSONResponse(
        status_code=200,
        content=QUERY_SERVICES.get_execution_answers(
            execution_id,
            page=page,
            page_size=page_size,
        ),
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
        async with aclosing(QUERY_SERVICES.stream_execution_events(execution_id)) as stream:
            async for event in stream:
                await websocket.send_json(event)

                if event.get("status") in TERMINAL_STATUSES:
                    break
    except WebSocketDisconnect:
        pass
    except CommandRouterConnectionError as error:
        await _safe_send_error(
            websocket,
            execution_id,
            error.message,
            details=getattr(error, "detail", None),
        )
    except json.JSONDecodeError:
        await _safe_send_error(
            websocket,
            execution_id,
            "Invalid JSON received from the command router stream.",
        )


async def _safe_send_error(
    websocket: WebSocket,
    execution_id: str,
    message: str,
    *,
    details: str | None = None,
) -> None:
    try:
        payload = {
            "execution_id": execution_id,
            "status": "error",
            "message": message,
        }
        if details:
            payload["details"] = details
        await websocket.send_json(payload)
    except (WebSocketDisconnect, RuntimeError):
        pass


def _proxy_json_content(response: Response) -> Any:
    try:
        content = response.json()
    except ValueError:
        return {"content": response.text}

    if isinstance(content, dict) and "error" in content and "message" not in content:
        content = {**content, "message": content["error"]}

    return content
