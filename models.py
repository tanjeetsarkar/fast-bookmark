from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class BookMarks(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[Optional[str]]
    url: Mapped[Optional[str]]
    date_created: Mapped[datetime] = mapped_column(default=datetime.now())
    date_modified: Mapped[datetime] = mapped_column(default=datetime.now())
