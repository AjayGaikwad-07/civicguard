import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReportStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    AI_TRIAGE = "AI_TRIAGE"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    FORWARDED_POLICE = "FORWARDED_POLICE"
    FORWARDED_MUNICIPAL = "FORWARDED_MUNICIPAL"
    CLOSED_VALID = "CLOSED_VALID"
    CLOSED_INVALID = "CLOSED_INVALID"


class ReportCategory(str, enum.Enum):
    LITTERING = "LITTERING"
    DUMPING = "DUMPING"
    VANDALISM = "VANDALISM"
    FIGHTING = "FIGHTING"
    HARASSMENT = "HARASSMENT"
    PARKING = "PARKING"
    OTHER = "OTHER"
    UNCLASSIFIED = "UNCLASSIFIED"


class ReportUrgency(str, enum.Enum):
    URGENT = "URGENT"
    CIVIC = "CIVIC"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"


class FileType(str, enum.Enum):
    VIDEO = "VIDEO"
    IMAGE = "IMAGE"


def _enum(enum_cls: type[enum.Enum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda members: [member.value for member in members],
        native_enum=True,
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    total_reward_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reports_submitted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reports_accepted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    is_blocked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    reports: Mapped[list["Report"]] = relationship(back_populates="reporter")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ReportStatus] = mapped_column(
        _enum(ReportStatus, "report_status"),
        nullable=False,
        default=ReportStatus.RECEIVED,
    )
    category: Mapped[ReportCategory] = mapped_column(
        _enum(ReportCategory, "report_category"),
        nullable=False,
        default=ReportCategory.UNCLASSIFIED,
    )
    urgency: Mapped[ReportUrgency] = mapped_column(
        _enum(ReportUrgency, "report_urgency"),
        nullable=False,
        default=ReportUrgency.LOW_CONFIDENCE,
    )
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    location_text: Mapped[str | None] = mapped_column(String(512), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    file_type: Mapped[FileType] = mapped_column(_enum(FileType, "file_type"), nullable=False)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ai_triage_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ai_confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    assigned_station: Mapped[str | None] = mapped_column(String(255), nullable=True)
    case_reference: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reward_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_flagged_false_report: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    reporter: Mapped[User | None] = relationship(back_populates="reports")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="report")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    performed_by: Mapped[str] = mapped_column(String(64), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    report: Mapped[Report] = relationship(back_populates="audit_logs")
