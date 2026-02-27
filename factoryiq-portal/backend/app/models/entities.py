import uuid
from sqlalchemy import String, Float, Integer, Date, DateTime, Text, ForeignKey, Enum, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from app.models.base import AuditedSoftDeleteMixin, RoleName, LifecycleState


class Role(AuditedSoftDeleteMixin, Base):
    __tablename__ = "roles"
    name: Mapped[RoleName] = mapped_column(Enum(RoleName), unique=True)
    users: Mapped[list["User"]] = relationship(back_populates="role")


class CustomerAccount(AuditedSoftDeleteMixin, Base):
    __tablename__ = "customer_accounts"
    name: Mapped[str] = mapped_column(String(120), unique=True)


class User(AuditedSoftDeleteMixin, Base):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("roles.id"))
    customer_account_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("customer_accounts.id"), nullable=True)
    role: Mapped[Role] = relationship(back_populates="users")


class Program(AuditedSoftDeleteMixin, Base):
    __tablename__ = "programs"
    name: Mapped[str] = mapped_column(String(120))
    customer_account_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("customer_accounts.id"))
    health_status: Mapped[str] = mapped_column(String(20), default="Green")


class Project(AuditedSoftDeleteMixin, Base):
    __tablename__ = "projects"
    name: Mapped[str] = mapped_column(String(120))
    program_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("programs.id"))
    customer_account_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("customer_accounts.id"))
    planned_end: Mapped[Date | None] = mapped_column(Date, nullable=True)
    actual_end: Mapped[Date | None] = mapped_column(Date, nullable=True)


class Milestone(AuditedSoftDeleteMixin, Base):
    __tablename__ = "milestones"
    name: Mapped[str] = mapped_column(String(120))
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("projects.id"))
    planned_date: Mapped[Date] = mapped_column(Date)
    actual_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    critical_path: Mapped[bool] = mapped_column(default=False)


class SiteFacility(AuditedSoftDeleteMixin, Base):
    __tablename__ = "site_facilities"
    name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(200))


class WorkOrder(AuditedSoftDeleteMixin, Base):
    __tablename__ = "work_orders"
    code: Mapped[str] = mapped_column(String(100), unique=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    site_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("site_facilities.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Open")
    qty_planned: Mapped[int] = mapped_column(Integer, default=0)
    qty_completed: Mapped[int] = mapped_column(Integer, default=0)


class OperationStation(AuditedSoftDeleteMixin, Base):
    __tablename__ = "operation_stations"
    work_order_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("work_orders.id"))
    name: Mapped[str] = mapped_column(String(120))
    yield_rate: Mapped[float] = mapped_column(Float, default=0)


class BOM(AuditedSoftDeleteMixin, Base):
    __tablename__ = "boms"
    project_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("projects.id"))
    version: Mapped[str] = mapped_column(String(30), default="A")


class BOMItem(AuditedSoftDeleteMixin, Base):
    __tablename__ = "bom_items"
    bom_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("boms.id"))
    part_number: Mapped[str] = mapped_column(String(80))
    quantity: Mapped[int] = mapped_column(Integer, default=1)


class Document(AuditedSoftDeleteMixin, Base):
    __tablename__ = "documents"
    customer_account_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("customer_accounts.id"))
    title: Mapped[str] = mapped_column(String(160))
    object_key: Mapped[str] = mapped_column(String(255))


class Revision(AuditedSoftDeleteMixin, Base):
    __tablename__ = "revisions"
    document_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("documents.id"))
    revision_no: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class ECOECR(AuditedSoftDeleteMixin, Base):
    __tablename__ = "eco_ecrs"
    project_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    change_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="Open")


class Supplier(AuditedSoftDeleteMixin, Base):
    __tablename__ = "suppliers"
    name: Mapped[str] = mapped_column(String(120), unique=True)
    score: Mapped[float] = mapped_column(Float, default=0)


class PurchaseOrder(AuditedSoftDeleteMixin, Base):
    __tablename__ = "purchase_orders"
    po_number: Mapped[str] = mapped_column(String(80), unique=True)
    supplier_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("suppliers.id"))
    status: Mapped[str] = mapped_column(String(50), default="Open")


class InventoryItem(AuditedSoftDeleteMixin, Base):
    __tablename__ = "inventory_items"
    sku: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(String(200))
    quantity: Mapped[int] = mapped_column(Integer, default=0)


class Shipment(AuditedSoftDeleteMixin, Base):
    __tablename__ = "shipments"
    tracking_number: Mapped[str] = mapped_column(String(100), unique=True)
    purchase_order_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("purchase_orders.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="In Transit")


class Forecast(AuditedSoftDeleteMixin, Base):
    __tablename__ = "forecasts"
    customer_account_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("customer_accounts.id"))
    period: Mapped[str] = mapped_column(String(40))
    demand: Mapped[int] = mapped_column(Integer)


class NCR(AuditedSoftDeleteMixin, Base):
    __tablename__ = "ncrs"
    title: Mapped[str] = mapped_column(String(160))
    state: Mapped[LifecycleState] = mapped_column(Enum(LifecycleState), default=LifecycleState.open)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)


class CAPA(AuditedSoftDeleteMixin, Base):
    __tablename__ = "capas"
    ncr_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("ncrs.id"), nullable=True)
    assignee: Mapped[str | None] = mapped_column(String(120), nullable=True)
    state: Mapped[LifecycleState] = mapped_column(Enum(LifecycleState), default=LifecycleState.open)
    effectiveness_notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class Audit(AuditedSoftDeleteMixin, Base):
    __tablename__ = "audits"
    topic: Mapped[str] = mapped_column(String(160))
    scheduled_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)


class RMA(AuditedSoftDeleteMixin, Base):
    __tablename__ = "rmas"
    case_number: Mapped[str] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(50), default="Open")


class RepairCase(AuditedSoftDeleteMixin, Base):
    __tablename__ = "repair_cases"
    rma_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("rmas.id"))
    status: Mapped[str] = mapped_column(String(50), default="In Progress")


class WarrantyClaim(AuditedSoftDeleteMixin, Base):
    __tablename__ = "warranty_claims"
    rma_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("rmas.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0)


class SparePartOrder(AuditedSoftDeleteMixin, Base):
    __tablename__ = "spare_part_orders"
    part_number: Mapped[str] = mapped_column(String(80))
    quantity: Mapped[int] = mapped_column(Integer, default=1)


class EOLNotice(AuditedSoftDeleteMixin, Base):
    __tablename__ = "eol_notices"
    part_number: Mapped[str] = mapped_column(String(80))
    effective_date: Mapped[Date | None] = mapped_column(Date, nullable=True)


class Notification(AuditedSoftDeleteMixin, Base):
    __tablename__ = "notifications"
    user_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message: Mapped[str] = mapped_column(String(255))
    read: Mapped[bool] = mapped_column(default=False)


class AuditLog(AuditedSoftDeleteMixin, Base):
    __tablename__ = "audit_logs"
    source: Mapped[str] = mapped_column(String(60))
    action: Mapped[str] = mapped_column(String(120))
    details: Mapped[str] = mapped_column(Text)
