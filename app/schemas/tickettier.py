import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TicketTierCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(..., ge=0, description="The price of the ticket tier")
    capacity: int = Field(..., gt=0, description="The capacity of the ticket tier")

class TicketTierRead(BaseModel):
    id: uuid.UUID = Field(..., description="The ID of the ticket tier")
    name: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(..., ge=0, description="The price of the ticket tier")
    capacity: int = Field(..., gt=0, description="The capacity of the ticket tier")
    event_id: uuid.UUID = Field(..., description="The ID of the event")
    available_seats: int = Field(..., description="The number of available seats for the ticket tier")
    created_at: datetime = Field(..., description="The date and time the ticket tier was created")
    updated_at: datetime = Field(..., description="The date and time the ticket tier was updated")

class TicketTierUpdate(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    capacity: int | None = None