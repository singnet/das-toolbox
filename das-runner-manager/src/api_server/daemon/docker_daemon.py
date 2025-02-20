from fastapi import HTTPException
from docker import from_env

client = from_env()

def up():
    try:
        client.ping()
        return {"status": "ok", "message": "Docker daemon is running"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Docker daemon error: {str(e)}")
