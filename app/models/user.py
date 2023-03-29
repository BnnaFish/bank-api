from datetime import datetime

from sqlalchemy import func, BIGINT, String, Identity
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        BIGINT, Identity(always=True), init=False, primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        default=None,
        init=False,
    )
    email: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(30))
    lastname: Mapped[str] = mapped_column(String(30))
