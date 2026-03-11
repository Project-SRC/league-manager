from datetime import date
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.user.driver import Driver
from src.schemas.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from src.schemas.league_relations import LeagueTeam


class Team(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "team"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    founded: Mapped[date | None] = mapped_column(DateTime, nullable=True)
    team_chief: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=True
    )
    logo: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_points: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_races: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    championships_won: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    drivers: Mapped[list[Driver]] = relationship(
        "Driver", back_populates="team", foreign_keys="Driver.current_team"
    )
    contracts: Mapped[list[Contract]] = relationship(
        "Contract", back_populates="team"
    )
    league_teams: Mapped[list[LeagueTeam]] = relationship(
        "LeagueTeam", back_populates="team"
    )


class Contract(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contract"

    team_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team.id"), nullable=True
    )
    driver_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("driver.id"), nullable=True
    )
    terminated_at: Mapped[date | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    team: Mapped[Team | None] = relationship("Team", back_populates="contracts")
    driver: Mapped[Driver | None] = relationship("Driver", back_populates="contracts")
