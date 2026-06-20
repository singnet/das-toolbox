from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from services_init import CONFIG_SERVICES, WEB_CONFIG
from shared.internal.configuration_constants import CONSTANTS
from shared.dtos.configuration_entries_dto import ConfigurationEntriesDto

router = APIRouter(prefix="/config", tags=["Configuration"])

@router.post("")
async def save_config(configuration_entries : ConfigurationEntriesDto):
    result = await CONFIG_SERVICES.save_config(configuration_entries)    
    WEB_CONFIG.load_config_dictionary()

    return JSONResponse(
        status_code=200,
        content=result
    )

@router.get("")
async def get_config():
    return JSONResponse(
        status_code=200,
        content={
            "content": WEB_CONFIG.config_dictionary
        }
    )

@router.get("/defaults")
async def get_config_defaults():
    return JSONResponse(
        status_code=200,
        content={
            "content": CONSTANTS
        }
    )