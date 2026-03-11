from uuid import UUID as PyUUID

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.league.league import League
from src.models.team.team import Team
from src.models.track.track import Track
from src.models.user.driver import Driver
from src.schemas.base import Base, TimestampMixin, UUIDMixin


class LeagueTeam(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "league_team"

    league_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("league.id"), nullable=False
    )
    team_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team.id"), nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    league: Mapped[League] = relationship("League", back_populates="league_teams")
    team: Mapped[Team] = relationship("Team", back_populates="league_teams")


class LeagueDriver(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "league_driver"

    league_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("league.id"), nullable=False
    )
    driver_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("driver.id"), nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    league: Mapped[League] = relationship("League", back_populates="league_drivers")
    driver: Mapped[Driver] = relationship("Driver", back_populates="league_drivers")


class LeagueTrack(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "league_track"

    league_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("league.id"), nullable=False
    )
    track_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("track.id"), nullable=False
    )
    order_index: Mapped[int] = mapped_column(Integer, nullable=True, default=0)

    league: Mapped[League] = relationship("League", back_populates="league_tracks")
    track: Mapped[Track] = relationship("Track", back_populates="league_tracks")
