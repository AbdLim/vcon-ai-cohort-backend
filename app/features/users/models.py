from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime
from sqlalchemy.sql import func
from datetime import datetime
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.features.auth.models import Auth

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationship to auth credentials
    auth: Mapped["Auth"] = relationship(back_populates="profile", uselist=False)
