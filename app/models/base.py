import datetime

from sqlalchemy import TIMESTAMP, MetaData
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

metadata_obj = MetaData()


class Base(MappedAsDataclass, DeclarativeBase):
    """Subclasses will be converted to dataclasses."""

    metadata = metadata_obj
    type_annotation_map = {
        datetime.datetime: TIMESTAMP(timezone=True),
    }
