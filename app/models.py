"""SQLAlchemy ORM models for Space Bounty Hunters."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class WantedCriminal(Base):
    """Wanted criminal model representing bounties across the galaxy."""

    __tablename__ = "wanted_criminals"
    __table_args__ = (
        CheckConstraint("difficulty >= 1 AND difficulty <= 10", name="check_difficulty_1_to_10"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nickname: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    reward: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    last_known_coordinates: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)
    armed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_crew: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    escape_master: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # One-to-many relationship: One criminal has multiple hunt logs
    hunt_logs: Mapped[list["HuntLog"]] = relationship(
        "HuntLog",
        back_populates="criminal",
        cascade="all, delete-orphan",
        order_by="HuntLog.created_at.desc()",
    )


class HuntLog(Base):
    """Journal entry representing an encounter/capture attempt by a bounty hunter."""

    __tablename__ = "hunt_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    criminal_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("wanted_criminals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Many-to-one relationship back to WantedCriminal
    criminal: Mapped["WantedCriminal"] = relationship(
        "WantedCriminal",
        back_populates="hunt_logs",
    )
