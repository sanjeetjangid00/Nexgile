from datetime import date, datetime
from pydantic import BaseModel


class BaseOut(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    created_by: str
    is_deleted: bool

    model_config = {"from_attributes": True}


class Pagination(BaseModel):
    skip: int = 0
    limit: int = 50


class ProgramIn(BaseModel):
    name: str
    customer_account_id: str


class ProjectIn(BaseModel):
    name: str
    program_id: str
    customer_account_id: str
    planned_end: date | None = None
    actual_end: date | None = None


class MilestoneIn(BaseModel):
    name: str
    project_id: str
    planned_date: date
    actual_date: date | None = None
    critical_path: bool = False


class WorkOrderIn(BaseModel):
    code: str
    project_id: str | None = None
    site_id: str | None = None
    status: str = "Open"
    qty_planned: int = 0
    qty_completed: int = 0


class POIn(BaseModel):
    po_number: str
    supplier_id: str
    status: str = "Open"


class RMAIn(BaseModel):
    case_number: str
    status: str = "Open"
