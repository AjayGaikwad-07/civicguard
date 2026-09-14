import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database import get_db
from app.models import AuditLog, FileType, Report, ReportCategory, ReportStatus, ReportUrgency
from app.schemas import ReportUploadResponse

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

ALLOWED_EXTENSIONS = {
    "mp4": FileType.VIDEO,
    "mov": FileType.VIDEO,
    "avi": FileType.VIDEO,
    "jpg": FileType.IMAGE,
    "jpeg": FileType.IMAGE,
    "png": FileType.IMAGE,
}

ALLOWED_TYPES_MESSAGE = (
    "File type not allowed. Accepted types: mp4, mov, avi, jpg, jpeg, png."
)


def _parse_captured_at(value: str | None) -> datetime | None:
    if value is None or not value.strip():
        return None
    raw = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="captured_at must be a valid ISO-8601 datetime string.",
        ) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _next_case_reference(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    prefix = f"CG-{year}-"
    last = db.execute(
        select(Report.case_reference)
        .where(Report.case_reference.like(f"{prefix}%"))
        .order_by(Report.case_reference.desc())
        .with_for_update()
    ).scalar_one_or_none()
    sequence = 1
    if last:
        sequence = int(last.rsplit("-", 1)[-1]) + 1
    return f"{prefix}{sequence:05d}"


@router.post("/upload", response_model=ReportUploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    location_text: str | None = Form(None),
    captured_at: str | None = Form(None),
    db: Session = Depends(get_db),
) -> ReportUploadResponse:
    filename = file.filename or ""
    extension = Path(filename).suffix.lower().lstrip(".")
    file_type = ALLOWED_EXTENSIONS.get(extension)
    if file_type is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ALLOWED_TYPES_MESSAGE)

    content = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum size of {settings.MAX_FILE_SIZE_MB} MB.",
        )
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    file_hash = hashlib.sha256(content).hexdigest()

    uploaded_at = datetime.now(timezone.utc)
    dest_dir = Path(settings.UPLOAD_DIR) / uploaded_at.strftime("%Y-%m-%d")
    dest_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4()}.{extension}"
    dest_path = dest_dir / stored_name
    dest_path.write_bytes(content)

    captured = _parse_captured_at(captured_at)
    location = location_text.strip() if location_text and location_text.strip() else None

    try:
        case_reference = _next_case_reference(db)
        report = Report(
            reporter_id=None,
            status=ReportStatus.RECEIVED,
            category=ReportCategory.UNCLASSIFIED,
            urgency=ReportUrgency.LOW_CONFIDENCE,
            latitude=latitude,
            longitude=longitude,
            location_text=location,
            file_path=str(dest_path.resolve()),
            file_hash=file_hash,
            file_type=file_type,
            captured_at=captured,
            uploaded_at=uploaded_at,
            case_reference=case_reference,
        )
        db.add(report)
        db.flush()
        db.add(
            AuditLog(
                report_id=report.id,
                action="REPORT_UPLOADED",
                performed_by="system",
                old_value=None,
                new_value=case_reference,
            )
        )
        db.commit()
        db.refresh(report)
    except Exception:
        db.rollback()
        dest_path.unlink(missing_ok=True)
        raise

    return ReportUploadResponse(
        case_reference=report.case_reference,
        status=report.status,
        message="Report received. You will be notified of updates.",
    )
