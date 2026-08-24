import asyncio
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from shared.enums.metric_scope import MetricScope
from services_init import METRICS_SERVICES

router = APIRouter(prefix="/metrics", tags=["Metrics"])

@router.get("")
async def fetch_initial_info(metric_scope: MetricScope = Query(...), host: str = Query(...)):
    result = await METRICS_SERVICES.load_server_metrics(metric_scope, host)
    return JSONResponse(
        status_code=200,
        content={"content": result}
    )

@router.get("/collection")
async def get_collection_status(server_ip: str = Query(...)):
    result = METRICS_SERVICES.get_collection_status(server_ip)
    return JSONResponse(
        status_code=200,
        content={"content": result}
    )

@router.post("/collection")
async def set_collection_enabled(
    server_ip: str = Query(...),
    enabled: bool = Query(...),
):
    result = METRICS_SERVICES.set_collection_enabled(server_ip, enabled)
    return JSONResponse(
        status_code=200,
        content={"content": result}
    )

@router.delete("/history/{server_ip}")
async def delete_server_history(server_ip: str):
    result = METRICS_SERVICES.delete_server_metrics(server_ip)
    return JSONResponse(
        status_code=200,
        content={"content": result}
    )

@router.delete("/history")
async def delete_history(unused_only: bool = Query(False)):
    if unused_only:
        result = METRICS_SERVICES.delete_unused_server_metrics()
    else:
        result = METRICS_SERVICES.delete_all_server_metrics()

    return JSONResponse(
        status_code=200,
        content={"content": result}
    )

@router.websocket("/live-ws")
async def stream_server_metrics(
    websocket: WebSocket,
    metric_scope: MetricScope,
    host: str
):
    await websocket.accept()
    
    try:
        async for metric in METRICS_SERVICES.stream_server_metrics(metric_scope, host):
            try:
                await websocket.send_json(metric)
            except (WebSocketDisconnect, RuntimeError):
                break

            if metric.get("type") == "error":
                await asyncio.sleep(0.5)
                try:
                    await websocket.close(code=1011, reason="Internal Stream Error")
                except RuntimeError:
                    pass
                return
                
    except WebSocketDisconnect:
        pass