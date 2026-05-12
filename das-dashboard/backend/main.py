from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, WebSocket, WebSocketDisconnect, UploadFile, File



from shared.enums.action_types import ActionTypes
from shared.enums.metric_scope import MetricScope
from shared.dtos.dashboard_action_dto import DashboardActionDTO
from shared.dtos.dashboard_profile_dto import DashboardProfileDto
from shared.dtos.dashboard_get_metrics_dto import GetMetricsDto

from services.container_services import ContainerServices
from services.profile_services import ProfileServices
from services.metrics_services import MetricsServices

BASE_ENDPOINT = "/dashboard"

CONTAINER_SERVICES = ContainerServices()
PROFILE_SERVICES = ProfileServices()
METRICS_SERVICES = MetricsServices()

dashboard_app = FastAPI()

dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### Dashboard Action Endpoints (Start, Stop or Restart a container/service)
@dashboard_app.post(f"{BASE_ENDPOINT}/service")
def execute_server_action(action : ActionTypes, action_request: DashboardActionDTO):

    match action:

        case ActionTypes.START:
            result = CONTAINER_SERVICES.start_das_cli_container(action_request)
            return JSONResponse(status_code=200, content={"message": "Command ran succesfully with no errors.", "cli_message": result})

        case ActionTypes.STOP:
            result = CONTAINER_SERVICES.stop_das_cli_container(action_request)
            return JSONResponse(status_code=200, content={"message": "Command ran succesfully with no errors.", "cli_message": result})

        case ActionTypes.RESTART:
            result = CONTAINER_SERVICES.restart_das_cli_container(action_request)
            return JSONResponse(status_code=200, content={"message": "Command ran succesfully with no errors.", "cli_message": result})

        case _:
            return JSONResponse(
                status_code=422,
                content={"msg": "Invalid specified command, please verify documentation before usage."}
            )


### UI Profile Endpoints (Create SSH Profile/Get profile and config info)
@dashboard_app.post(f"{BASE_ENDPOINT}/profile")
async def create_user_profile(
    dashboard_profile: DashboardProfileDto = Depends(DashboardProfileDto.as_form)
):
    await PROFILE_SERVICES.save_dashboard_profile(dashboard_profile)

    return JSONResponse(status_code=201, content={"message":"The user's SSH profile was created sucessfully."})

@dashboard_app.post(f"{BASE_ENDPOINT}/config")
async def save_config(config_file: UploadFile = File(...)):

    result = await PROFILE_SERVICES.save_config(config_file)

    return JSONResponse(
        status_code=201,
        content=result
    )


### Dashboard Data Endpoints (Get static info, real-time, specific service)
@dashboard_app.get(f"{BASE_ENDPOINT}/metrics")
async def fetch_initial_info(metric_scope: MetricScope, target_ip : str):
    result = await METRICS_SERVICES.load_server_metrics(metric_scope, target_ip)

    return JSONResponse(
        status_code=200,
        content=result
    )


@dashboard_app.websocket(f"{BASE_ENDPOINT}/metrics/stream")
async def stream_server_metrics(websocket: WebSocket, metric_scope: MetricScope, target_ip : str):
    await websocket.accept()

    try:
        async for metric in METRICS_SERVICES.stream_server_metrics(metric_scope):
            await websocket.send_json(metric)
    except WebSocketDisconnect:
        pass