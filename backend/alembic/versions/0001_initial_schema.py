"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-27

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("route_number", sa.String(length=32), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("vehicle_number", sa.String(length=32), nullable=False, unique=True),
        sa.Column("registration_number", sa.String(length=32), nullable=False, unique=True),
        sa.Column("vehicle_type", sa.String(length=32), nullable=False, server_default="bus"),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="OFFLINE"),
        sa.Column("route_id", sa.Integer(), sa.ForeignKey("routes.id"), nullable=False),
        sa.Column("latest_latitude", sa.Float(), nullable=True),
        sa.Column("latest_longitude", sa.Float(), nullable=True),
        sa.Column("latest_speed", sa.Float(), nullable=True),
        sa.Column("latest_gps_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "route_points",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("route_id", sa.Integer(), sa.ForeignKey("routes.id"), nullable=False, index=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("sequence_number", sa.Integer(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("username", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("email", sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=128), nullable=False),
        sa.Column("route_id", sa.Integer(), sa.ForeignKey("routes.id"), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "gps_tracking",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("vehicle_id", sa.Integer(), sa.ForeignKey("vehicles.id"), nullable=False, index=True),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_gps_vehicle_timestamp", "gps_tracking", ["vehicle_id", "timestamp"])


def downgrade() -> None:
    op.drop_index("ix_gps_vehicle_timestamp", table_name="gps_tracking")
    op.drop_table("gps_tracking")
    op.drop_table("users")
    op.drop_table("route_points")
    op.drop_table("vehicles")
    op.drop_table("routes")
