from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models import FileType, ReportCategory, ReportStatus, ReportUrgency


class ReportUploadResponse(BaseModel):
    case_reference: str
    status: ReportStatus
    message: str


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID | None
    status: ReportStatus
    category: ReportCategory
    urgency: ReportUrgency
    latitude: float | None
    longitude: float | None
    location_text: str | None
    file_path: str
    file_hash: str
    file_type: FileType
    captured_at: datetime | None
    uploaded_at: datetime
    ai_triage_result: dict | None
    ai_confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    assigned_station: str | None
    case_reference: str
    reviewer_notes: str | None
    reward_points: int
    is_flagged_false_report: bool


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    name: str | None
    is_verified: bool
    total_reward_points: int
    reports_submitted: int
    reports_accepted: int
    created_at: datetime
    is_blocked: bool


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    action: str
    performed_by: str
    old_value: str | None
    new_value: str | None
    timestamp: datetime
