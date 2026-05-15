from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from shared.enums.action_types import ActionTypes
from shared.enums.metric_scope import MetricScope

from services.container_services import ContainerServices
from services.profile_services import ProfileServices
from services.metrics_services import MetricsServices

BASE_ENDPOINT = "/dashboard"


CONTAINER_SERVICES = ContainerServices()
PROFILE_SERVICES = ProfileServices()
METRICS_SERVICES = MetricsServices()

dashboard_app = FastAPI(title="DAS Dashboard API")

dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_target_info(ip: str) -> dict:
    profile = PROFILE_SERVICES.load_dashboard_profile_safe()
    return {
        "ip": ip,
        "username": profile.get("profile_username") if profile else None,
        "key_file": profile.get("profile_ssh_keypath") if profile else None
    }

@dashboard_app.post(f"{BASE_ENDPOINT}/service")
async def execute_server_action(
    action: ActionTypes, 
    targetIp: str = Query(...), 
    targetService: str = Query(...),
    containerName: str = Query(...),
):
    target_info = get_target_info(targetIp)
    
    result = CONTAINER_SERVICES.manage_container(
        service_name=targetService,
        action=action.value,
        target_info=target_info,
        container_name=containerName,
    )

    return JSONResponse(
        status_code=200, 
        content={
            "message": f"Service {action.value} command executed.",
            "stdout": result.stdout if hasattr(result, 'stdout') else str(result)
        }
    )


@dashboard_app.post(f"{BASE_ENDPOINT}/profile")
async def create_user_profile(
    sshUsername: str = Form(...),
    sshKeyFile: UploadFile = File(...)
):
    msg = await PROFILE_SERVICES.save_dashboard_profile(sshUsername, sshKeyFile)
    return JSONResponse(status_code=201, content={"message": msg})

@dashboard_app.post(f"{BASE_ENDPOINT}/config")
async def save_config(config_file: UploadFile = File(...)):
    result = await PROFILE_SERVICES.save_config(config_file)
    return JSONResponse(status_code=201, content=result)


@dashboard_app.get(f"{BASE_ENDPOINT}/metrics")
async def fetch_initial_info(
    metric_scope: MetricScope = Query(...), 
    target_ip: str = Query(...)
):
    target_info = get_target_info(target_ip)
    result = await METRICS_SERVICES.load_server_metrics(metric_scope, target_info)
    return JSONResponse(status_code=200, content=result)

@dashboard_app.websocket(f"{BASE_ENDPOINT}/metrics/stream")
async def stream_server_metrics(
    websocket: WebSocket, 
    metric_scope: MetricScope = Query(...), 
    target_ip: str = Query(...)
):
    await websocket.accept()
    target_info = get_target_info(target_ip)
    
    try:
        async for metric in METRICS_SERVICES.stream_server_metrics(metric_scope, target_info):
            await websocket.send_json(metric)
    except (WebSocketDisconnect, Exception):
        pass