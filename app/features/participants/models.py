from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.sql import func
from datetime import datetime
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.features.cohorts.models import Cohort
    from app.features.users.models import User

class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cohort_id: Mapped[int] = mapped_column(ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False)

    role: Mapped[str] = mapped_column(String, default="student", server_default="student", nullable=False) # e.g. student, coach, mentor
    
    # Aggregated metrics for easy querying
    sessions_attended: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    average_talk_time_pct: Mapped[float] = mapped_column(Float, default=0.0, server_default="0.0")
    health_score: Mapped[float | None] = mapped_column(Float, nullable=True) # e.g., 0-100 score risk model
    
    # Store aggregated history or external IDs
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="participants")
    cohort: Mapped["Cohort"] = relationship(back_populates="participants")
