import uuid
from fastapi import APIRouter
from app.dependencies import TicketTierServiceDep
from app.schemas.tickettier import TicketTierCreate, TicketTierRead

router = APIRouter()

@router.post("/events/{event_id}/tiers", status_code=201, response_model=TicketTierRead)
async def create_tier(event_id: uuid.UUID, service: TicketTierServiceDep, data: TicketTierCreate) -> TicketTierRead:
    return service.create_tier(event_id, data)

@router.get("/events/{event_id}/tiers", response_model=list[TicketTierRead])
async def get_tiers(event_id: uuid.UUID, service: TicketTierServiceDep) -> list[TicketTierRead]:
    return service.get_tiers_by_event(event_id)