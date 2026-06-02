from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, WebSocketException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from shared.enums.action_types import ActionTypes
from shared.enums.metric_scope import MetricScope

from shared.internal.web_configuration import WebConfiguration

from shared.exceptions.exception_handlers import AppExceptionHandlers
from shared.exceptions.custom_exceptions import WebSocketError, WebSocketMessageDecodeError, WebSocketStreamEmpty

from services.container_services import ContainerServices
from services.profile_services import ProfileServices
from services.metrics_services import MetricsServices
from services.config_services import ConfigServices
from services.database_services import DatabaseServices

from shared.utils.storage_check import validate_persistent_storage

import asyncio

WEB_CONFIG = WebConfiguration()

CONTAINER_SERVICES = ContainerServices(WEB_CONFIG)
DATABASE_SERVICES = DatabaseServices(WEB_CONFIG)
PROFILE_SERVICES = ProfileServices(WEB_CONFIG)
METRICS_SERVICES = MetricsServices(WEB_CONFIG)
CONFIG_SERVICES = ConfigServices(WEB_CONFIG)

@asynccontextmanager
async def lifespan(app: FastAPI):

    validate_persistent_storage()

    WEB_CONFIG.load_user_profile()
    WEB_CONFIG.load_config_dictionary()

    yield

dashboard_app = FastAPI(
    title="DAS Dashboard API",
    lifespan=lifespan,
)

AppExceptionHandlers(dashboard_app)

dashboard_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dashboard_app.post("/services/atomdb/metta/upload")
async def upload_metta_file(host: str = Query(...), force_overwrite : bool = Query(...), knowledge_base_file: UploadFile = File(...)):
    saved_path = await DATABASE_SERVICES.save_metta_file(
        host=host,
        knowledge_file=knowledge_base_file,
        force_overwrite=force_overwrite,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Metta file uploaded sucesssfully.",
            "saved_path": saved_path,
        }
    )


@dashboard_app.post("/services/atomdb/metta/load")
async def load_metta_file(host: str = Query(...), metta_file_path: str = Query(...)):
    result = DATABASE_SERVICES.load_metta_file_into_db(
        host=host,
        metta_file_path=metta_file_path,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Knowledge file loaded successfully.",
            "loaded_path": metta_file_path,
            "result": result,
        }
    )


@dashboard_app.post("/services/orchestration/start")
async def start_orchestration(host: str = Query(...)):
    result = CONTAINER_SERVICES.orchestrate_architecture(
        action=ActionTypes.START,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Architecture started successfully.",
            "results": result,
        }
    )


@dashboard_app.post("/services/orchestration/stop")
async def stop_orchestration(host: str = Query(...)):
    result = CONTAINER_SERVICES.orchestrate_architecture(
        host=host,
        action=ActionTypes.STOP,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Architecture stopped successfully.",
            "results": result,
        }
    )


@dashboard_app.post("/services/atomdb/start")
async def start_databases(host: str = Query(...)):
    result = CONTAINER_SERVICES.manage_container(
        host=host,
        container_name=None,
        command="db",
        action=ActionTypes.START,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Databases started successfully.",
            "result": result,
        }
    )


@dashboard_app.post("/services/atomdb/stop")
async def stop_databases(host: str = Query(...)):
    result = CONTAINER_SERVICES.manage_container(
        host=host,
        container_name=None,
        command="db",
        action=ActionTypes.STOP,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Databases stopped successfully.",
            "result": result,
        }
    )

@dashboard_app.post("/services/{container_name}/start")
async def start_service(container_name: str, host: str = Query(...)):
    result = CONTAINER_SERVICES.manage_container(
        host=host,
        container_name=container_name,
        action=ActionTypes.START,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Service {result} started successfully.",
            "result": result,
        }
    )


@dashboard_app.post("/services/{container_name}/stop")
async def stop_service(container_name: str, host: str = Query(...)):
    result = CONTAINER_SERVICES.manage_container(
        host=host,
        container_name=container_name,
        action=ActionTypes.STOP,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Service {container_name} stopped successfully.",
            "result": result,
        }
    )


@dashboard_app.post("/services/{container_name}/restart")
async def restart_service(container_name: str, host: str = Query(...)):
    result = CONTAINER_SERVICES.manage_container(
        host=host,
        container_name=container_name,
        action=ActionTypes.RESTART,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Service {container_name} restarted successfully.",
            "result": result,
        }
    )

@dashboard_app.post("/profile")
async def create_user_profile(sshUsername: str = Form(...), sshKeyFile: UploadFile = File(...)):
    result = await PROFILE_SERVICES.save_dashboard_profile(sshUsername,sshKeyFile,)
    WEB_CONFIG.load_user_profile()

    return JSONResponse(
        status_code=200,
        content={
            "message": result,
        }
    )


@dashboard_app.get("/profile")
async def get_user_profile():
    return JSONResponse(
        status_code=200,
        content={
            "message": WEB_CONFIG.user_profile
        }
    )


@dashboard_app.post("/config")
async def save_config(config_file: UploadFile = File(...),):
    result = await CONFIG_SERVICES.save_config(config_file)
    WEB_CONFIG.load_config_dictionary()
    
    return JSONResponse(
        status_code=200,
        content={
            "message": result["message"],
            "stdout": result["stdout"]
        }
    )


@dashboard_app.get("/config")
async def get_config():

    return JSONResponse(
        status_code=200,
        content={
            "content": WEB_CONFIG.config_dictionary
        }
    )

@dashboard_app.get("/metrics")
async def fetch_initial_info(metric_scope: MetricScope = Query(...), host: str = Query(...)):

    result = await METRICS_SERVICES.load_server_metrics(
        metric_scope,
        host,
    )

    return JSONResponse(
        status_code=200,
        content={
            "content": result
        }
    )


@dashboard_app.websocket("/metrics/live-ws")
async def stream_server_metrics(
    websocket: WebSocket,
    metric_scope: MetricScope,
    host: str
):
    await websocket.accept()

    async for metric in METRICS_SERVICES.stream_server_metrics(metric_scope, host):
        await websocket.send_json(metric)

        if metric.get("type") == "error":
            await asyncio.sleep(1)

            await websocket.close(
                code=1011,
                reason="Internal WebSocket Error"
            )

            return