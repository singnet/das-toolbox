from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services_init import CONFIG_SERVICES, WEB_CONFIG
from shared.dtos.configuration_entries_dto import ConfigurationEntriesDto
from shared.internal.configuration_constants import ATOMDB_TEMPLATES, CONSTANTS

router = APIRouter(prefix="/config", tags=["Configuration"])


class ContextMappingBody(BaseModel):
    content: Optional[str] = None
    path: Optional[str] = None


@router.post("/save")
async def save_config(configuration_entries: ConfigurationEntriesDto):
    result = await CONFIG_SERVICES.save_config(configuration_entries)

    return JSONResponse(status_code=200, content=result)


@router.get("/saved")
async def config_saved():
    return JSONResponse(
        status_code=200,
        content={"saved": await CONFIG_SERVICES.has_saved_config()},
    )


@router.post("/export")
async def export_config():
    try:
        nested = await CONFIG_SERVICES.export_config()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return JSONResponse(
        status_code=200,
        content={"content": nested},
    )


@router.post("/export/targets")
async def export_targets():
    try:
        targets = await CONFIG_SERVICES.export_targets()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return JSONResponse(status_code=200, content=targets)


@router.post("/export/scp/{ip}")
async def export_config_scp(ip: str):
    try:
        result = await CONFIG_SERVICES.export_config_scp(ip)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return JSONResponse(status_code=200, content=result)


@router.post("/load")
async def load_config(nested_config: dict[str, Any]):
    flat = await CONFIG_SERVICES.load_config(nested_config)

    return JSONResponse(
        status_code=200,
        content={"content": flat},
    )


@router.post("/adapter/context-mapping")
async def save_context_mapping(body: ContextMappingBody):
    result = await CONFIG_SERVICES.save_context_mapping(body.content, body.path)

    return JSONResponse(status_code=200, content=result)


@router.get("")
async def get_config():
    return JSONResponse(
        status_code=200,
        content={
            "content": WEB_CONFIG.config_dictionary
        },
    )


@router.get("/defaults")
async def get_config_defaults():
    return JSONResponse(
        status_code=200,
        content={
            "content": CONSTANTS,
            "atomdb_templates": ATOMDB_TEMPLATES,
        },
    )
