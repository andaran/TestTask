"""create prices table

Revision ID: 9edbdd76716a
Revises:
Create Date: 2026-10-16 11:51:12.156588

"""

from typing import TYPE_CHECKING

import sqlalchemy as sa
from alembic import op

if TYPE_CHECKING:
    from collections.abc import Sequence

revision: str = "9edbdd76716a"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column(
            "ticker", sa.Enum("btc_usd", "eth_usd", name="ticker"), nullable=False
        ),
        sa.Column("price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("timestamp", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("price >= 0", name=op.f("ck_prices_price_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_prices")),
    )
    op.create_index(
        op.f("ix_prices_ticker_timestamp"),
        "prices",
        ["ticker", "timestamp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_prices_ticker_timestamp"), table_name="prices")
    op.drop_table("prices")
    sa.Enum(name="ticker").drop(op.get_bind())
