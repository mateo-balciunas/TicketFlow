

from datetime import UTC, datetime
import uuid
from app.core.exceptions import EventConflictError, EventNotFoundError, TicketTierNotFoundError
from app.repositories.event_repository import EventRepository
from app.repositories.tickettier_repository import TicketTierRepository
from app.schemas.tickettier import TicketTierCreate, TicketTierRead, TicketTierUpdate


class TicketTierService:
    def __init__(self, tickettier_repository: TicketTierRepository, event_repository: EventRepository) -> None:
        self.tickettier_repository = tickettier_repository
        self.event_repository = event_repository

    def create_tier(self, event_id: uuid.UUID, data: TicketTierCreate) -> TicketTierRead:
        event = self.event_repository.get_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event with id {event_id} not found")

        existing_tiers = self.tickettier_repository.get_by_event(event_id)
        if any(t.name == data.name for t in existing_tiers):
            raise EventConflictError(f"Ticket tier with name {data.name} already exists for event {event_id}")
        new_tier = TicketTierRead(
            id=uuid.uuid4(),
            event_id=event_id,
            available_seats=data.capacity,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            **data.model_dump(),
        )
        return self.tickettier_repository.create(new_tier)

    def get_tier(self, tier_id: uuid.UUID) -> TicketTierRead:
        tier = self.tickettier_repository.get_by_id(tier_id)
        if not tier:
            raise TicketTierNotFoundError(f"Ticket tier with id {tier_id} not found")
        return tier
    
    def get_tiers_by_event(self, event_id: uuid.UUID) -> list[TicketTierRead]:
        tiers = self.tickettier_repository.get_by_event(event_id)
        if len(tiers) == 0:
            return []
        return tiers

    def update_tier(self, tier_id: uuid.UUID, data: TicketTierUpdate) -> TicketTierRead:
        existing_tier = self.tickettier_repository.get_by_id(tier_id)
        if not existing_tier:
            raise TicketTierNotFoundError(f"Ticket tier with id {tier_id} not found")
        updated_tier = self.tickettier_repository.update(tier_id, data)
        if updated_tier is None:
            raise TicketTierNotFoundError(f"Ticket tier with id {tier_id} not found")
        return updated_tier

    def delete_tier(self, tier_id: uuid.UUID) -> None:
        existing_tier = self.tickettier_repository.get_by_id(tier_id)
        if not existing_tier:
            raise TicketTierNotFoundError(f"Ticket tier with id {tier_id} not found")
        self.tickettier_repository.delete(tier_id)