"""create all tables

Revision ID: 06798e1e6c20
Revises: 504a47d91487
Create Date: 2026-03-11 10:36:22.797466

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "06798e1e6c20"
down_revision: str | None = "504a47d91487"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("password", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("nickname", sa.Text(), nullable=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("profile_picture", sa.Text(), nullable=True),
        sa.Column("is_manager", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("is_driver", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("is_steward", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("is_admin", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("steward_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terminated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "country",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("abbreviation", sa.Text(), nullable=False),
        sa.Column("flag", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terminated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "team",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("founded", sa.DateTime(), nullable=True),
        sa.Column("team_chief", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("logo", sa.Text(), nullable=True),
        sa.Column("total_points", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_races", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("championships_won", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terminated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "track",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("founded", sa.DateTime(), nullable=True),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("length_km", sa.Float(), nullable=False),
        sa.Column("number_curves", sa.Integer(), nullable=False),
        sa.Column("map_image", sa.Text(), nullable=True),
        sa.Column("record_time", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terminated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["country_id"], ["country.id"]),
    )

    op.create_table(
        "driver",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("current_team", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("total_podiums", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_points", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("total_races", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("championships_won", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("birth_date", sa.DateTime(), nullable=True),
        sa.Column("birth_place", sa.Text(), nullable=True),
        sa.Column("number", sa.String(10), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terminated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["country_id"], ["country.id"]),
        sa.ForeignKeyConstraint(["current_team"], ["team.id"]),
    )

    op.create_table(
        "manager",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )

    op.create_table(
        "steward",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
    )

    op.create_table(
        "contract",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("terminated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"]),
        sa.ForeignKeyConstraint(["driver_id"], ["driver.id"]),
    )

    op.create_table(
        "league",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("races", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("teams", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("drivers", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("points", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("doubled_points", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("prize", postgresql.JSONB(), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "race",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("track_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("number_laps", sa.Integer(), nullable=True),
        sa.Column("race_time", sa.Text(), nullable=True),
        sa.Column("driver_max", sa.Integer(), nullable=True, server_default="20"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["track_id"], ["track.id"]),
    )

    op.create_table(
        "participation",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("race_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["race_id"], ["race.id"]),
        sa.ForeignKeyConstraint(["driver_id"], ["driver.id"]),
    )

    op.create_table(
        "league_team",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("league_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["league_id"], ["league.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"]),
    )

    op.create_table(
        "league_driver",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("league_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["league_id"], ["league.id"]),
        sa.ForeignKeyConstraint(["driver_id"], ["driver.id"]),
    )

    op.create_table(
        "league_track",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("league_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("track_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["league_id"], ["league.id"]),
        sa.ForeignKeyConstraint(["track_id"], ["track.id"]),
    )

    op.alter_column("user", "manager_id", server_default=None)
    op.alter_column("user", "driver_id", server_default=None)
    op.alter_column("user", "steward_id", server_default=None)


def downgrade() -> None:
    op.drop_table("league_track")
    op.drop_table("league_driver")
    op.drop_table("league_team")
    op.drop_table("participation")
    op.drop_table("race")
    op.drop_table("league")
    op.drop_table("contract")
    op.drop_table("steward")
    op.drop_table("manager")
    op.drop_table("driver")
    op.drop_table("track")
    op.drop_table("team")
    op.drop_table("country")
    op.drop_table("user")
