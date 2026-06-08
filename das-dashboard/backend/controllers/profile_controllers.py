from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from services_init import PROFILE_SERVICES, WEB_CONFIG

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.post("")
async def create_user_profile(sshUsername: str = Form(...), sshKeyFile: UploadFile = File(...)):
    result = await PROFILE_SERVICES.save_dashboard_profile(sshUsername, sshKeyFile)
    WEB_CONFIG.load_user_profile()
    return JSONResponse(
        status_code=200,
        content={
            "message": result,
        }
    )

@router.get("")
async def get_user_profile():
    return JSONResponse(
        status_code=200,
        content={
            "message": WEB_CONFIG.user_profile
        }
    )