from datetime import datetime
import uuid
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.enums import ReservationStatus
from sqlalchemy import Enum as SAEnum


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    tier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ticket_tiers.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[ReservationStatus] = mapped_column(SAEnum(ReservationStatus, native_enum=False))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)