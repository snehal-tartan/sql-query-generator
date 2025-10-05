from fastapi import APIRouter
from pydantic import BaseModel
from ..database import set_database_credentials, test_connection, is_connected


router = APIRouter(prefix="", tags=["auth"])


class DatabaseCredentials(BaseModel):
    host: str
    user: str
    password: str
    database: str
    port: int = 3306


@router.post("/connect_database")
async def connect_database(credentials: DatabaseCredentials):
    try:
        set_database_credentials(
            credentials.host,
            credentials.user,
            credentials.password,
            credentials.database,
            credentials.port,
        )
        if test_connection():
            return {"message": "Successfully connected to database", "status": "success"}
        else:
            return {"error": "Failed to connect to database", "status": "error"}
    except Exception as e:
        return {"error": f"Connection error: {str(e)}", "status": "error"}


@router.get("/database_status")
async def database_status():
    return {"connected": is_connected()}


