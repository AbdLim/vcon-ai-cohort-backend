from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.features.auth.models import Auth
    from app.features.cohorts.models import Organization
    from app.features.participants.models import Participant

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Optional link if user belongs fundamentally to one organization 
    # (can be expanded to many-to-many later if needed)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    auth: Mapped["Auth"] = relationship(back_populates="profile", uselist=False)
    organization: Mapped["Organization"] = relationship(back_populates="users")
    participants: Mapped[list["Participant"]] = relationship(back_populates="user")
