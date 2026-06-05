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