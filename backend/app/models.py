"""Database schema.

Scenario tables hold authored content (text as {"en": ..., "ru": ...}).
Session tables hold one simulation run. Fast-changing numeric state
(progress, indexes, overrides) lives in `sessions.state` so a clock tick
is a single-row update.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

JsonType = JSON().with_variant(JSONB(), "postgresql")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------- scenario


class Scenario(Base):
    __tablename__ = "scenarios"

    code: Mapped[str] = mapped_column(String(32), primary_key=True)
    title: Mapped[dict] = mapped_column(JsonType)
    description: Mapped[dict] = mapped_column(JsonType)
    weeks: Mapped[int] = mapped_column(Integer, default=12)
    currency: Mapped[str] = mapped_column(String(8), default="EUR")
    pm_rate: Mapped[float] = mapped_column(Float)
    material_budget: Mapped[float] = mapped_column(Float)
    other_budget: Mapped[float] = mapped_column(Float)


class Activity(Base):
    __tablename__ = "activities"
    __table_args__ = (UniqueConstraint("scenario_code", "no"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code", ondelete="CASCADE"))
    no: Mapped[int] = mapped_column(Integer)
    name: Mapped[dict] = mapped_column(JsonType)
    duration_days: Mapped[int] = mapped_column(Integer)
    effort_hours: Mapped[float] = mapped_column(Float)
    planned_cost: Mapped[float] = mapped_column(Float)
    milestone: Mapped[bool] = mapped_column(Boolean, default=False)


class Dependency(Base):
    __tablename__ = "dependencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code", ondelete="CASCADE"))
    activity_no: Mapped[int] = mapped_column(Integer)
    predecessor_no: Mapped[int] = mapped_column(Integer)


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = (UniqueConstraint("scenario_code", "no"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code", ondelete="CASCADE"))
    no: Mapped[int] = mapped_column(Integer)
    name: Mapped[dict] = mapped_column(JsonType)
    role: Mapped[dict] = mapped_column(JsonType)
    rate: Mapped[float] = mapped_column(Float)


class ResourceWeek(Base):
    """Planned availability: payroll, available, training, sick, holiday, other."""

    __tablename__ = "resource_weeks"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code", ondelete="CASCADE"))
    resource_no: Mapped[int] = mapped_column(Integer)
    week: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(16))


class DefaultAssignment(Base):
    __tablename__ = "default_assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code", ondelete="CASCADE"))
    activity_no: Mapped[int] = mapped_column(Integer)
    resource_no: Mapped[int] = mapped_column(Integer)
    percent: Mapped[int] = mapped_column(Integer)


class ScenarioEvent(Base):
    """Something that happens at a project time: mail, phone call or meeting.

    A mail/phone event lands in the inbox. A meeting is shown in the calendar.
    Any event may open a decision and may carry effects applied on delivery.
    """

    __tablename__ = "scenario_events"
    __table_args__ = (UniqueConstraint("scenario_code", "key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(32))
    week: Mapped[int] = mapped_column(Integer)
    weekday: Mapped[int] = mapped_column(Integer)
    hour: Mapped[int] = mapped_column(Integer)
    duration_h: Mapped[float] = mapped_column(Float, default=0)
    channel: Mapped[str] = mapped_column(String(16))
    sender: Mapped[dict] = mapped_column(JsonType)
    subject: Mapped[dict] = mapped_column(JsonType)
    body: Mapped[dict] = mapped_column(JsonType)
    effects: Mapped[dict] = mapped_column(JsonType, default=dict)
    decision_key: Mapped[str | None] = mapped_column(String(32), nullable=True)


class Decision(Base):
    __tablename__ = "decisions"
    __table_args__ = (UniqueConstraint("scenario_code", "key"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(32))
    prompt: Mapped[dict] = mapped_column(JsonType)
    default_option: Mapped[str] = mapped_column(String(16))
    deadline_hours: Mapped[int] = mapped_column(Integer, default=6)

    options: Mapped[list["DecisionOption"]] = relationship(
        cascade="all, delete-orphan", order_by="DecisionOption.key"
    )


class DecisionOption(Base):
    __tablename__ = "decision_options"

    id: Mapped[int] = mapped_column(primary_key=True)
    decision_id: Mapped[int] = mapped_column(ForeignKey("decisions.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(16))
    label: Mapped[dict] = mapped_column(JsonType)
    feedback: Mapped[dict] = mapped_column(JsonType)
    effects: Mapped[dict] = mapped_column(JsonType, default=dict)
    learning_point: Mapped[dict | None] = mapped_column(JsonType, nullable=True)


# ---------------------------------------------------------------- users


class User(Base):
    """A player signed in with Yandex ID or VK ID (VK, Odnoklassniki, Mail.ru).

    Exactly one of yandex_id / vk_id is set. avatar_id is a Yandex avatar id
    or, for VK users, a full avatar URL.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    yandex_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    vk_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    login: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ---------------------------------------------------------------- session


class SimSession(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("scenarios.code"))
    locale: Mapped[str] = mapped_column(String(8))
    config: Mapped[dict] = mapped_column(JsonType)
    status: Mapped[str] = mapped_column(String(16), default="ready")  # ready|running|paused|ended
    minutes: Mapped[float] = mapped_column(Float, default=0)
    last_tick_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    state: Mapped[dict] = mapped_column(JsonType)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    activity_no: Mapped[int] = mapped_column(Integer)
    resource_no: Mapped[int] = mapped_column(Integer)
    percent: Mapped[int] = mapped_column(Integer)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    event_key: Mapped[str] = mapped_column(String(32))
    minute: Mapped[float] = mapped_column(Float)
    read: Mapped[bool] = mapped_column(Boolean, default=False)


class SessionDecision(Base):
    __tablename__ = "session_decisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    decision_key: Mapped[str] = mapped_column(String(32))
    event_key: Mapped[str] = mapped_column(String(32))
    opened_minute: Mapped[float] = mapped_column(Float)
    deadline_minute: Mapped[float] = mapped_column(Float)
    postponed: Mapped[bool] = mapped_column(Boolean, default=False)
    option_key: Mapped[str | None] = mapped_column(String(16), nullable=True)
    resolved_by: Mapped[str | None] = mapped_column(String(8), nullable=True)  # team|auto
    resolved_minute: Mapped[float | None] = mapped_column(Float, nullable=True)


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    minute: Mapped[float] = mapped_column(Float)
    cost_idx: Mapped[float] = mapped_column(Float)
    schedule_idx: Mapped[float] = mapped_column(Float)
    quality_idx: Mapped[float] = mapped_column(Float)
    motivation_idx: Mapped[float] = mapped_column(Float)
    ac: Mapped[float] = mapped_column(Float)
    ev: Mapped[float] = mapped_column(Float)
    pv: Mapped[float] = mapped_column(Float)
    hours: Mapped[float] = mapped_column(Float)


class ActionLog(Base):
    __tablename__ = "action_log"
    __table_args__ = (UniqueConstraint("session_id", "client_action_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    client_action_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(32))
    payload: Mapped[dict] = mapped_column(JsonType, default=dict)
    minute: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
