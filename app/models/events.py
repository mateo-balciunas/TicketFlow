
from datetime import datetime
from decimal import Decimal
import uuid
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Numeric, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.enums import EventCategory, EventStatus


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column(DateTime)
    location: Mapped[str] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    organizer_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)
    category: Mapped[EventCategory] = mapped_column(SAEnum(EventCategory, native_enum=False))
    status: Mapped[EventStatus] = mapped_column(SAEnum(EventStatus, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)