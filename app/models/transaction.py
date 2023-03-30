import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BIGINT, CheckConstraint, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TransactionType(enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class Transaction(Base):
    __tablename__ = "transaction"

    uuid: Mapped[UUID] = mapped_column(
        init=False, primary_key=True, default_factory=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(), default=None, init=False, index=True
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
