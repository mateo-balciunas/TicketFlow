

import uuid
from datetime import UTC, datetime

from app.core.exceptions import EventNotFoundError
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventRead, EventStatus, EventUpdate


class EventService:
    def __init__(self, event_repository: EventRepository) -> None:
        self.event_repository = event_repository

    def create_event(self, data: EventCreate) -> EventRead:
        new_event = EventRead(
            id=uuid.uuid4(),
            organizer_id=uuid.uuid4(), # TODO: Add organizer id
            status=EventStatus.DRAFT,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            **data.model_dump(),
        )
        return self.event_repository.create(new_event)

    def get_event(self, event_id: uuid.UUID) -> EventRead:
        event = self.event_repository.get_by_id(event_id)
        if not event:
            raise EventNotFoundError(f"Event with id {event_id} not found")
        return event

    def get_events(
        self,
        status: EventStatus | None = None,
        from_date: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
        ) -> list[EventRead]:
        events = self.event_repository.get_all()
        if status is not None:
            events = [e for e in events if e.status == status]
        if from_date is not None:
            events = [e for e in events if e.date >= from_date]

        return events[offset: offset + limit]

    def update_event(self, event_id: uuid.UUID, data: EventUpdate) -> EventRead:
        existing_event = self.event_repository.get_by_id(event_id)
        if not existing_event:
            raise EventNotFoundError(f"Event with id {event_id} not found")
        updated_event = self.event_repository.update(event_id, data)
        if updated_event is None:
            raise EventNotFoundError(f"Event with id {event_id} not found")
        return updated_event

    def delete_event(self, event_id: uuid.UUID) -> None:
        existing_event = self.event_repository.get_by_id(event_id)
        if not existing_event:
            raise EventNotFoundError(f"Event with id {event_id} not found")
        self.event_repository.delete(event_id)