import enum
from datetime import datetime
from uuid import UUID, uuid4

import pytz
from sqlalchemy import BIGINT, CheckConstraint, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TransactionType(enum.Enum):
    DEPOSIT = "DEPOSIT"  # noqa: WPS115 Found upper-case constant in a class
    WITHDRAW = "WITHDRAW"  # noqa: WPS115 Found upper-case constant in a class


class Transaction(Base):
    __tablename__ = "transaction"

    uuid: Mapped[UUID] = mapped_column(
        init=False,
        primary_key=True,
        default_factory=uuid4,
    )
    # lambda is used cause it will be easy to test with freezegun
    # https://stackoverflow.com/a/58776798
    created_at: Mapped[datetime] = mapped_column(
        insert_default=lambda: datetime.now(pytz.utc),
        default=None,
        init=False,
        index=True,
    )
    type: Mapped[TransactionType]
    amount: Mapped[int] = mapped_column(
        BIGINT,
        CheckConstraint("amount > 0", name="positive_amount_check"),
    )
    balance_before: Mapped[int] = mapped_column(
        BIGINT,
        CheckConstraint("balance_before >= 0", name="positive_balance_before_check"),
    )
    balance_after: Mapped[int] = mapped_column(
        BIGINT,
        CheckConstraint("balance_after >= 0", name="positive_balance_after_check"),
    )
    wallet_uuid: Mapped[UUID] = mapped_column(Uuid, ForeignKey("wallet.uuid"))
