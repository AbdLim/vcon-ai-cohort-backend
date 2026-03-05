from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from datetime import datetime
from typing import TYPE_CHECKING
from app.db.base import Base

if TYPE_CHECKING:
    from app.features.cohorts.models import Cohort

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False, index=True)
    cohort_id: Mapped[int] = mapped_column(ForeignKey("cohorts.id", ondelete="CASCADE"), nullable=False)
    
    # The actual date the session took place
    session_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # State machine for processing (e.g. uploaded, processing, failed, completed)
    status: Mapped[str] = mapped_column(String, default="uploaded", server_default="uploaded", nullable=False)

    # Base file strings
    audio_file_url: Mapped[str | None] = mapped_column(String, nullable=True) # From S3/Cloudinary
    vcon_file_url: Mapped[str | None] = mapped_column(String, nullable=True) # From S3/Cloudinary

    # Cached insights for fast frontend rendering (saves having to fetch/parse the massive vCon object constantly)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    topics_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    action_items_json: Mapped[list | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # Relationships
    cohort: Mapped["Cohort"] = relationship(back_populates="sessions")
