from datetime import datetime
from typing import Any
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.track.track import Track
from src.models.user.driver import Driver
from src.schemas.base import Base, TimestampMixin, UUIDMixin
from src.schemas.league_relations import LeagueDriver, LeagueTeam, LeagueTrack
from src.utils.constants import DEFAULT_POINTS_DISTRIBUTION


class League(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "league"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    races: Mapped[list[PyUUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=True, default=list
    )
    teams: Mapped[list[PyUUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=True, default=list
    )
    drivers: Mapped[list[PyUUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=True, default=list
    )
    points: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=True, default=DEFAULT_POINTS_DISTRIBUTION
    )
    doubled_points: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    prize: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    league_teams: Mapped[list[LeagueTeam]] = relationship(
        "LeagueTeam", back_populates="league"
    )
    league_drivers: Mapped[list[LeagueDriver]] = relationship(
        "LeagueDriver", back_populates="league"
    )
    league_tracks: Mapped[list[LeagueTrack]] = relationship(
        "LeagueTrack", back_populates="league"
    )


class Race(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "race"

    track_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("track.id"), nullable=True
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    number_laps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    race_time: Mapped[str | None] = mapped_column(Text, nullable=True)
    driver_max: Mapped[int] = mapped_column(Integer, nullable=True, default=20)

    track: Mapped[Track | None] = relationship("Track", back_populates="races")
    participation: Mapped[list["Participation"]] = relationship(
        "Participation", back_populates="race"
    )


class Participation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "participation"

    race_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("race.id"), nullable=True
    )
    driver_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("driver.id"), nullable=True
    )
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    points: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    race: Mapped[Race | None] = relationship("Race", back_populates="participation")
    driver: Mapped[Driver | None] = relationship(
        "Driver", back_populates="participation"
    )
