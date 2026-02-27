import enum
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class RoleName(str, enum.Enum):
    admin = "Admin"
    program_manager = "Program Manager"
    engineer = "Engineer"
    quality = "Quality"
    supply_chain = "Supply Chain"
    service = "Service"
    customer_user = "Customer User"


class LifecycleState(str, enum.Enum):
    open = "Open"
    in_progress = "In Progress"
    closed = "Closed"


class AuditedSoftDeleteMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(120), default="system")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
