import uuid

from app.schemas.event import EventRead, EventUpdate


class EventRepository:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, EventRead] = {}

    def create(self, event: EventRead) -> EventRead:
        self._store[event.id] = event
        return event

    def get_by_id(self, id: uuid.UUID) -> EventRead | None:
        return self._store.get(id)

    def get_all(self) -> list[EventRead]:
        return list(self._store.values())

    def update(self, id: uuid.UUID, data: EventUpdate) -> EventRead | None:
        if id not in self._store:
            return None
        existing = self._store[id]
        updated = existing.model_copy(update=data.model_dump(exclude_unset=True))
        self._store[id] = updated
        return updated

    def delete(self, id: uuid.UUID) -> bool:
        if id not in self._store:
            return False
        del self._store[id]
        return True