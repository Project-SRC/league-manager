from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.track.track import Track
from src.models.user.driver import Driver
from src.schemas.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Country(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "country"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    abbreviation: Mapped[str] = mapped_column(Text, nullable=False)
    flag: Mapped[str | None] = mapped_column(Text, nullable=True)

    drivers: Mapped[list[Driver]] = relationship("Driver", back_populates="country")
    tracks: Mapped[list[Track]] = relationship("Track", back_populates="country")
