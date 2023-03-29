from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import BIGINT, CheckConstraint, func, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.models.base import Base


class Wallet(Base):
    __tablename__ = "wallet"

    uuid: Mapped[UUID] = mapped_column(
        init=False, primary_key=True, default_factory=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        init=False,
    )
    amount: Mapped[int] = mapped_column(
        CheckConstraint("amount >= 0", name="positive_amount_check"),
        default=0,
        init=False,
    )
    user_id: Mapped[int] = mapped_column(BIGINT, ForeignKey("user.id"))
