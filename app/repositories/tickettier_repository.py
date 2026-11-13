import uuid

from app.schemas.tickettier import TicketTierRead, TicketTierUpdate


class TicketTierRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, TicketTierRead] = {}

    def create(self, tier: TicketTierRead) -> TicketTierRead:
        self._store[tier.id] = tier
        return tier

    def get_by_id(self, tier_id: uuid.UUID) -> TicketTierRead | None:
        return self._store.get(tier_id)

    def get_by_event(self, event_id: uuid.UUID) -> list[TicketTierRead]:
        return [tier for tier in self._store.values() if tier.event_id == event_id]
    
    def update(self, tier_id: uuid.UUID, data: TicketTierUpdate) -> TicketTierRead | None:
        if tier_id not in self._store:
            return None
        existing = self._store[tier_id]
        updated = existing.model_copy(update=data.model_dump(exclude_unset=True))
        self._store[tier_id] = updated
        return updated
    
    def delete(self, tier_id: uuid.UUID) -> bool:
        if tier_id not in self._store:
            return False
        del self._store[tier_id]
        return True