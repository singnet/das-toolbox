from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from shared.enums.action_types import ActionTypes
from services_init import CONTAINER_SERVICES

router = APIRouter(prefix="/services", tags=["Orchestration & Services"])

@router.post("/orchestration/start")
def start_orchestration(services: list[str]):
    if not services:
        raise HTTPException(status_code=400, detail="At least one service is required.")

    result = CONTAINER_SERVICES.orchestrate_architecture(
        action=ActionTypes.START,
        services=services,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": "Architecture started successfully.",
            "results": result,
        }
    )

@router.post("/orchestration/stop")
def stop_orchestration(services: list[str]):
    if not services:
        raise HTTPException(status_code=400, detail="At least one service is required.")

    result = CONTAINER_SERVICES.orchestrate_architecture(
        action=ActionTypes.STOP,
        services=services,
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

@router.post("/{service_command}/start")
def start_service(service_command: str):

    result = CONTAINER_SERVICES.manage_container(
        container_name=service_command,
        action=ActionTypes.START,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Service {service_command} started successfully.",
            "result": result,
        }
    )

@router.post("/{service_command}/stop")
def stop_service(service_command: str):
    
    result = CONTAINER_SERVICES.manage_container(
        container_name=service_command,
        action=ActionTypes.STOP,
    )

    return JSONResponse(
        status_code=200,
        content={
            "message": f"Service {service_command} stopped successfully.",
            "result": result,
        }
    )

@router.post("/{service_command}/restart")
def restart_service(service_command: str):
    result = CONTAINER_SERVICES.manage_container(
        container_name=service_command,
        action=ActionTypes.RESTART,
    )
    return JSONResponse(
        status_code=200,
        content={
            "message": f"Service {service_command} restarted successfully.",
            "result": result,
        }
    )