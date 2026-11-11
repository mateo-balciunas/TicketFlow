import uuid
from fastapi import APIRouter
from app.dependencies import EventServiceDep
from app.schemas.event import EventCreate, EventRead, EventUpdate

router = APIRouter()

@router.post("/", status_code=201, response_model=EventRead)
async def create_event(service: EventServiceDep, data: EventCreate) -> EventRead:
    return service.create_event(data)

@router.get("/", response_model=list[EventRead])
async def get_events(service: EventServiceDep) -> list[EventRead]:
    return service.get_events()

@router.get("/{event_id}", response_model=EventRead)
async def get_event(event_id: uuid.UUID, service: EventServiceDep) -> EventRead:
    return service.get_event(event_id)

@router.patch("/{event_id}", response_model=EventRead)
async def update_event(event_id: uuid.UUID, service: EventServiceDep, data: EventUpdate) -> EventRead:
    return service.update_event(event_id, data)

@router.delete("/{event_id}", status_code=204)
async def delete_event(event_id: uuid.UUID, service: EventServiceDep) -> None:
    return service.delete_event(event_id)