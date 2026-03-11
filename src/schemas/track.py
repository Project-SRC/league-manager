from datetime import date
from uuid import UUID as PyUUID

from sqlalchemy import DateTime, Double, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.country import Country
from src.models.race.race import Race
from src.schemas.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin
from src.schemas.league_relations import LeagueTrack


class Track(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "track"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    founded: Mapped[date | None] = mapped_column(DateTime, nullable=True)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(Text, nullable=True)
    country_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("country.id"), nullable=True
    )
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    length_km: Mapped[float] = mapped_column(Double, nullable=False)
    number_curves: Mapped[int] = mapped_column(Integer, nullable=False)
    map_image: Mapped[str | None] = mapped_column(Text, nullable=True)
    record_time: Mapped[str | None] = mapped_column(Text, nullable=True)

    country: Mapped[Country | None] = relationship("Country", back_populates="tracks")
    races: Mapped[list[Race]] = relationship("Race", back_populates="track")
    league_tracks: Mapped[list[LeagueTrack]] = relationship(
        "LeagueTrack", back_populates="track"
    )
