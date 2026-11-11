from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from app.repositories.event_repository import EventRepository
from app.services.event_service import EventService

@lru_cache
def get_event_repository() -> EventRepository:
    return EventRepository()

def get_event_service(repo: Annotated[EventRepository, Depends(get_event_repository)]) -> EventService:
    return EventService(repo)

EventServiceDep = Annotated[EventService, Depends(get_event_service)]