from __future__ import annotations

from datetime import datetime
from uuid import UUID as PyUUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.schemas.base import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from src.schemas.league_relations import LeagueDriver


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    nickname: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    profile_picture: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_manager: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_driver: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_steward: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

    manager_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("manager.id"), nullable=True
    )
    driver_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("driver.id"), nullable=True
    )
    steward_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("steward.id"), nullable=True
    )

    driver_profile: Mapped[Driver | None] = relationship(
        "Driver", foreign_keys=[driver_id], viewonly=True
    )
    manager_profile: Mapped[Manager | None] = relationship(
        "Manager", foreign_keys=[manager_id], viewonly=True
    )
    steward_profile: Mapped[Steward | None] = relationship(
        "Steward", foreign_keys=[steward_id], viewonly=True
    )


class Driver(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "driver"

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    country_id: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("country.id"), nullable=True
    )
    current_team: Mapped[PyUUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("team.id"), nullable=True
    )

    total_podiums: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_points: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    total_races: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    championships_won: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    birth_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    birth_place: Mapped[str | None] = mapped_column(Text, nullable=True)
    number: Mapped[str] = mapped_column(String(10), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

    user: Mapped[User] = relationship("User", foreign_keys=[user_id], viewonly=True)
    country: Mapped[Country | None] = relationship(
        "Country", back_populates="drivers", viewonly=True
    )
    team: Mapped[Team | None] = relationship("Team", back_populates="drivers", viewonly=True)
    contracts: Mapped[list[Contract]] = relationship(
        "Contract", back_populates="driver", viewonly=True
    )
    participation: Mapped[list[Participation]] = relationship(
        "Participation", back_populates="driver", viewonly=True
    )
    league_drivers: Mapped[list[LeagueDriver]] = relationship(
        "LeagueDriver", back_populates="driver", viewonly=True
    )
    team: Mapped["Team | None"] = relationship("Team", back_populates="drivers", viewonly=True)
    contracts: Mapped[list["Contract"]] = relationship(
        "Contract", back_populates="driver", viewonly=True
    )
    participation: Mapped[list["Participation"]] = relationship(
        "Participation", back_populates="driver", viewonly=True
    )
    league_drivers: Mapped[list["LeagueDriver"]] = relationship(
        "LeagueDriver", back_populates="driver", viewonly=True
    )


class Manager(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "manager"

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship("User", foreign_keys=[user_id], viewonly=True)


class Steward(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "steward"

    user_id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("user.id"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    deactivated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship("User", foreign_keys=[user_id], viewonly=True)
