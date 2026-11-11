from datetime import datetime, UTC
from decimal import Decimal
from enum import StrEnum
import uuid
from pydantic import BaseModel, field_validator, Field


class EventStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    CANCELLED = "cancelled"

class EventCategory(StrEnum):
    CONFERENCE = "conference"
    MEETING = "meeting"
    WORKSHOP = "workshop"
    SEMINAR = "seminar"
    WEBINAR = "webinar"
    OTHER = "other"
    
class EventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=1000)
    date: datetime = Field(..., description="The date and time of the event")
    location: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(..., description="The price of the event")
    category: EventCategory = Field(..., description="The category of the event")

    @field_validator("date")
    @classmethod
    def date_must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.now(UTC):
            raise ValueError("Date must be in the future")
        return v

class EventRead(BaseModel):
    id: uuid.UUID = Field(..., description="The ID of the event")
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=1000)
    date: datetime = Field(..., description="The date and time of the event")
    location: str = Field(..., min_length=1, max_length=255)
    organizer_id: uuid.UUID = Field(..., description="The ID of the organizer")
    price: Decimal = Field(..., description="The price of the event")
    category: EventCategory = Field(..., description="The category of the event")
    status: EventStatus = Field(..., description="The status of the event")
    created_at: datetime = Field(..., description="The date and time the event was created")
    updated_at: datetime = Field(..., description="The date and time the event was updated")

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    date: datetime | None = None
    location: str | None = None
    price: Decimal | None = None
    category: EventCategory | None = None
    status: EventStatus | None = None