from __future__ import annotations

from datetime import datetime
from typing import Generator

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    JSON,
    ForeignKey,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session

from .settings import settings


class Base(DeclarativeBase):
    pass


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    kind: Mapped[str] = mapped_column(String(20))

    events: Mapped[list["Event"]] = relationship(back_populates="asset")


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("trace_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(36))
    source: Mapped[str] = mapped_column(String(50))
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    kind: Mapped[str] = mapped_column(String(20))
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    payload: Mapped[dict] = mapped_column(JSON)

    asset: Mapped[Asset] = relationship(back_populates="events")


class Indicator(Base):
    __tablename__ = "indicators"
    __table_args__ = (UniqueConstraint("asset_id", "key", "ts"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    key: Mapped[str] = mapped_column(String(50))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    value: Mapped[float] = mapped_column()
    meta: Mapped[dict] = mapped_column(JSON, default={})


class Score(Base):
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    total: Mapped[int] = mapped_column(Integer)
    breakdown: Mapped[dict] = mapped_column(JSON)
    version: Mapped[str] = mapped_column(String(20))


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
