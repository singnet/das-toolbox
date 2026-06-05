from fastapi import APIRouter
from fastapi.responses import JSONResponse
from shared.enums.action_types import ActionTypes
from services_init import CONTAINER_SERVICES

router = APIRouter(prefix="/services", tags=["Orchestration & Services"])

@router.post("/orchestration/start")
def start_orchestration():
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

@router.post("/orchestration/stop")
def stop_orchestration():
    result = CONTAINER_SERVICES.orchestrate_architecture(
        action=ActionTypes.STOP,
    )
    return JSONResponse(
        status_code=200,
        content={
            "message": "Architecture stopped successfully.",
            "results": result,
        }
    )

@router.post("/atomdb/start")
def start_databases():
    result = CONTAINER_SERVICES.manage_container(
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

@router.post("/atomdb/stop")
def stop_databases():
    result = CONTAINER_SERVICES.manage_container(
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

@router.post("/{container_name}/start")
def start_service(container_name: str):
    result = CONTAINER_SERVICES.manage_container(
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

@router.post("/{container_name}/stop")
def stop_service(container_name: str):
    result = CONTAINER_SERVICES.manage_container(
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

@router.post("/{container_name}/restart")
def restart_service(container_name: str):
    result = CONTAINER_SERVICES.manage_container(
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