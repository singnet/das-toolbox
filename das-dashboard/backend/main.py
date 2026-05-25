from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from shared.enums.action_types import ActionTypes
from shared.enums.metric_scope import MetricScope
from shared.internal.web_configuration import WebConfiguration

from services.container_services import ContainerServices
from services.profile_services import ProfileServices
from services.metrics_services import MetricsServices
from services.config_services import ConfigServices
from services.database_services import DatabaseServices

BASE_ENDPOINT = "/dashboard"

WEB_CONFIG = WebConfiguration()

CONTAINER_SERVICES = ContainerServices(WEB_CONFIG)
DATABASE_SERVICES = DatabaseServices(WEB_CONFIG)
PROFILE_SERVICES = ProfileServices(WEB_CONFIG)
METRICS_SERVICES = MetricsServices(WEB_CONFIG)
CONFIG_SERVICES = ConfigServices(WEB_CONFIG)


@asynccontextmanager
async def lifespan(app: FastAPI):

    WEB_CONFIG.load_user_profile()
    WEB_CONFIG.load_config_dictionary()

    yield


dashboard_app = FastAPI(
    title="DAS Dashboard API",
    lifespan=lifespan,
)

dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_target_info(host: str):

    return {
        "ip": host,
        "username": WEB_CONFIG.user_profile.get("profile_username"),
        "key_file": WEB_CONFIG.user_profile.get("profile_ssh_keypath"),
    }


@dashboard_app.post(f"{BASE_ENDPOINT}/service")
async def execute_action_on_service(
    action: ActionTypes = Query(...),
    host: str = Query(...),
    container: str = Query(...),
):

    result = CONTAINER_SERVICES.manage_container(
        host=host,
        container_name=container,
        action=action,
    )

    return {
        "message": f"Container {action.value} executed.",
        "result": result,
    }


@dashboard_app.post(f"{BASE_ENDPOINT}/orchestrate")
async def execute_action_on_architecture(
    action: ActionTypes = Query(...),
    host: str = Query(...),
):

    result = CONTAINER_SERVICES.orchestrate_architecture(
        host=host,
        action=action,
    )

    return {
        "message": f"Architecture {action.value} executed.",
        "results": result,
    }


@dashboard_app.post(f"{BASE_ENDPOINT}/orchestrate/dbs")
async def execute_action_on_dbs(
    action: ActionTypes = Query(...),
    host: str = Query(...),
):

    result = CONTAINER_SERVICES.manage_container(
        host=host,
        container_name=None,
        command="db",
        action=action,
    )

    return {
        "message": f"Databases {action.value} executed.",
        "result": result,
    }

@dashboard_app.post(f"{BASE_ENDPOINT}/service/dbs/save")
async def save_metta_file(
    host: str = Query(...),
    knowledge_base_file: UploadFile = File(...),
):

    saved_path = await DATABASE_SERVICES.save_metta_file(
        host=host,
        knowledge_file=knowledge_base_file,
    )

    return {
        "message": "Knowledge file saved successfully.",
        "saved_path": saved_path,
    }


@dashboard_app.post(f"{BASE_ENDPOINT}/service/dbs/load")
async def load_metta_file(
    host: str = Query(...),
    metta_file_path: str = Query(...),
):

    result = DATABASE_SERVICES.load_metta_file_into_db(
        host=host,
        metta_file_path=metta_file_path,
    )

    return {
        "message": "Knowledge file loaded into database successfully.",
        "result": result,
        "loaded_path": metta_file_path,
    }

@dashboard_app.post(f"{BASE_ENDPOINT}/profile")
async def create_user_profile(
    sshUsername: str = Form(...),
    sshKeyFile: UploadFile = File(...),
):

    result = await PROFILE_SERVICES.save_dashboard_profile(
        sshUsername,
        sshKeyFile,
    )

    WEB_CONFIG.load_user_profile()

    return {"message": result}


@dashboard_app.post(f"{BASE_ENDPOINT}/config")
async def save_config(
    config_file: UploadFile = File(...),
):

    result = await CONFIG_SERVICES.save_config(config_file)

    WEB_CONFIG.load_config_dictionary()

    return result


@dashboard_app.get(f"{BASE_ENDPOINT}/metrics")
async def fetch_initial_info(
    metric_scope: MetricScope = Query(...),
    host: str = Query(...),
):

    return await METRICS_SERVICES.load_server_metrics(
        metric_scope,
        build_target_info(host),
    )


@dashboard_app.websocket(f"{BASE_ENDPOINT}/metrics/stream")
async def stream_server_metrics(
    websocket: WebSocket,
    metric_scope: MetricScope = Query(...),
    host: str = Query(...),
):

    await websocket.accept()

    try:

        async for metric in METRICS_SERVICES.stream_server_metrics(
            metric_scope,
            build_target_info(host),
        ):
            await websocket.send_json(metric)

    except (WebSocketDisconnect, Exception):
        pass