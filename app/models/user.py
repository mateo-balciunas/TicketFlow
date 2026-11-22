from datetime import datetime
import uuid
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base
from app.models.enums import UserRole
from sqlalchemy import Enum as SAEnum

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, native_enum=False))
    created_at: Mapped[datetime] = mapped_column(DateTime)
