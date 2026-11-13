import uuid
from datetime import datetime

from fastapi import APIRouter, Query

from app.dependencies import EventServiceDep
from app.schemas.event import EventCreate, EventRead, EventStatus, EventUpdate

router = APIRouter()

@router.post("/", status_code=201, response_model=EventRead)
async def create_event(service: EventServiceDep, data: EventCreate) -> EventRead:
    return service.create_event(data)

@router.get("/", response_model=list[EventRead])
async def get_events(service: EventServiceDep, status: EventStatus | None = None, from_date: datetime | None = None,
                    limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0)
) -> list[EventRead]:
    return service.get_events(status=status, from_date=from_date, limit=limit, offset=offset)

@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: uuid.UUID, service: EventServiceDep,) -> EventRead:
    return service.get_event(event_id)

@router.patch("/{event_id}", response_model=EventRead)
async def update_event(event_id: uuid.UUID, service: EventServiceDep, data: EventUpdate) -> EventRead:
    return service.update_event(event_id, data)

@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: uuid.UUID, service: EventServiceDep) -> None:
    return service.delete_event(event_id)