from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from services_init import CONFIG_SERVICES, WEB_CONFIG

router = APIRouter(prefix="/config", tags=["Configuration"])

@router.post("")
async def save_config(config_file: UploadFile = File(...)):
    result = await CONFIG_SERVICES.save_config(config_file)
    WEB_CONFIG.load_config_dictionary()
    return JSONResponse(
        status_code=200,
        content={
            "message": result["message"],
            "stdout": result["stdout"]
        }
    )

@router.get("")
async def get_config():
    return JSONResponse(
        status_code=200,
        content={
            "content": WEB_CONFIG.config_dictionary
        }
    )