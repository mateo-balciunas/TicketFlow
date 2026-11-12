from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from app.repositories.event_repository import EventRepository
from app.services.event_service import EventService
from app.repositories.tickettier_repository import TicketTierRepository
from app.services.tickettier_service import TicketTierService

@lru_cache
def get_event_repository() -> EventRepository:
    return EventRepository()

def get_event_service(repo: Annotated[EventRepository, Depends(get_event_repository)]) -> EventService:
    return EventService(repo)

EventServiceDep = Annotated[EventService, Depends(get_event_service)]

@lru_cache
def get_tickettier_repository() -> TicketTierRepository:
    return TicketTierRepository()

def get_tickettier_service(tier_repo: Annotated[TicketTierRepository, Depends(get_tickettier_repository)], event_repo: Annotated[EventRepository, Depends(get_event_repository)]) -> TicketTierService:
    return TicketTierService(tier_repo, event_repo)

TicketTierServiceDep = Annotated[TicketTierService, Depends(get_tickettier_service)]