from typing import Annotated
from fastapi import FastAPI, Depends
from app.schemas.health import HealthResponse
from app.core.config import Settings, get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

SettingsDep = Annotated[Settings, Depends(get_settings)]

@app.get('/health', response_model=HealthResponse)
async def get_health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(status="ok", app_name= settings.app_name)