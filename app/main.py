from typing import Annotated
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import EventConflictError, EventNotFoundError, TicketTierNotFoundError
from app.schemas.health import HealthResponse
from app.core.config import Settings, get_settings
from app.api.v1.events import router as events_router
from app.api.v1.tickettiers import router as tickettiers_router

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(events_router, prefix="/api/v1/events", tags=["events"])
app.include_router(tickettiers_router, prefix="/api/v1")

SettingsDep = Annotated[Settings, Depends(get_settings)]

@app.get('/health', response_model=HealthResponse)
async def get_health(settings: SettingsDep) -> HealthResponse:
    return HealthResponse(status="ok", app_name= settings.app_name)

@app.exception_handler(EventNotFoundError)
async def event_not_found_handler(request: Request, exc: EventNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})

@app.exception_handler(EventConflictError)
async def event_conflict_error_handler(request: Request, exc: EventConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})

@app.exception_handler(TicketTierNotFoundError)
async def ticket_tier_not_found_error_handler(request: Request, exc: TicketTierNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})