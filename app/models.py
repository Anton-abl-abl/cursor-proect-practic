import json
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def _now() -> datetime:
    return datetime.now()


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now, onupdate=_now, nullable=False
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    keywords: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    key_points: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    search_text: Mapped[str] = mapped_column(Text, nullable=False, default="")

    @property
    def keyword_list(self) -> list[str]:
        return _load_strings(self.keywords)

    @property
    def tag_list(self) -> list[str]:
        return _load_strings(self.tags)

    @property
    def key_point_list(self) -> list[str]:
        return _load_strings(self.key_points)


def _load_strings(raw: str) -> list[str]:
    loaded = json.loads(raw)
    if not isinstance(loaded, list) or any(not isinstance(item, str) for item in loaded):
        raise ValueError("Поле анализа заметки повреждено")
    return loaded
