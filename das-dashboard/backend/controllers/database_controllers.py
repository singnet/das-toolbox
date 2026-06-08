from fastapi import APIRouter, Query, UploadFile, File
from fastapi.responses import JSONResponse
from services_init import DATABASE_SERVICES

router = APIRouter(prefix="/services/atomdb", tags=["Database"])

@router.post("/metta/upload")
async def upload_metta_file(
    host: str = Query(...), 
    force_overwrite: bool = Query(...), 
    knowledge_base_file: UploadFile = File(...)
):
    saved_path = await DATABASE_SERVICES.save_metta_file(
        host=host,
        knowledge_file=knowledge_base_file,
        force_overwrite=force_overwrite,
    )
    return JSONResponse(
        status_code=200,
        content={
            "message": "Metta file uploaded successfully.",
            "saved_path": saved_path,
        }
    )

@router.post("/metta/load")
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