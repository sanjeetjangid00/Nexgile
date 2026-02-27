from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud.base import CRUDBase
from app.db.session import get_db
from app.models.entities import (
    Program, Project, Milestone, WorkOrder, PurchaseOrder, InventoryItem, Shipment,
    Forecast, NCR, CAPA, Audit, RMA, RepairCase, WarrantyClaim, SparePartOrder,
    Document, Revision, AuditLog, User
)
from app.schemas.common import ProgramIn, ProjectIn, MilestoneIn, WorkOrderIn, POIn, RMAIn
from app.services.project_service import calculate_project_health
from app.services.notification_service import notify
from app.services.storage_service import put_object, presigned_download
from app.workers.tasks import generate_report

router = APIRouter()
crud = {
    "programs": CRUDBase(Program), "projects": CRUDBase(Project), "milestones": CRUDBase(Milestone),
    "work_orders": CRUDBase(WorkOrder), "purchase_orders": CRUDBase(PurchaseOrder), "rmas": CRUDBase(RMA),
}


def _get_or_404(model, db: Session, obj_id: str, name: str):
    try:
        pk = uuid.UUID(obj_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid {name} id")
    obj = db.get(model, pk)
    if not obj or obj.is_deleted:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return obj


@router.post('/auth/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username, User.is_deleted.is_(False)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return {'access_token': create_access_token(str(user.id)), 'token_type': 'bearer'}


@router.get('/health')
def health():
    return {'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}


@router.post('/programs')
def create_program(payload: ProgramIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud['programs'].create(db, {**payload.model_dump(), 'created_by': user.email})


@router.get('/programs')
def list_programs(skip: int = 0, limit: int = 50, customer_account_id: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    filters = {'customer_account_id': customer_account_id or user.customer_account_id}
    return crud['programs'].list(db, skip, limit, filters)


@router.post('/projects')
def create_project(payload: ProjectIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud['projects'].create(db, {**payload.model_dump(), 'created_by': user.email})
    health = calculate_project_health(db, str(obj.id))
    notify(db, f'Project {obj.name} created with health {health}', created_by=user.email)
    return obj


@router.get('/projects')
def list_projects(skip: int = 0, limit: int = 50, program_id: str | None = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    filters = {'program_id': program_id, 'customer_account_id': user.customer_account_id}
    return crud['projects'].list(db, skip, limit, filters)


@router.post('/milestones')
def create_milestone(payload: MilestoneIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = crud['milestones'].create(db, {**payload.model_dump(), 'created_by': user.email})
    if payload.actual_date and payload.actual_date > payload.planned_date:
        notify(db, f'Milestone delayed: {payload.name}', created_by=user.email)
    return obj


@router.get('/projects/{project_id}/health')
def project_health(project_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return {'project_id': project_id, 'health': calculate_project_health(db, project_id)}


@router.post('/work-orders')
def create_work_order(payload: WorkOrderIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud['work_orders'].create(db, {**payload.model_dump(), 'created_by': user.email})



@router.get('/rmas')
def list_rmas(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud['rmas'].list(db, skip, limit)


@router.put('/programs/{program_id}')
def update_program(program_id: str, payload: ProgramIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = _get_or_404(Program, db, program_id, 'Program')
    return crud['programs'].update(db, obj, payload.model_dump())


@router.delete('/programs/{program_id}')
def delete_program(program_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = _get_or_404(Program, db, program_id, 'Program')
    crud['programs'].soft_delete(db, obj)
    return {'status': 'deleted'}


@router.put('/projects/{project_id}')
def update_project(project_id: str, payload: ProjectIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = _get_or_404(Project, db, project_id, 'Project')
    return crud['projects'].update(db, obj, payload.model_dump())


@router.delete('/projects/{project_id}')
def delete_project(project_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = _get_or_404(Project, db, project_id, 'Project')
    crud['projects'].soft_delete(db, obj)
    return {'status': 'deleted'}


@router.put('/milestones/{milestone_id}')
def update_milestone(milestone_id: str, payload: MilestoneIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = _get_or_404(Milestone, db, milestone_id, 'Milestone')
    return crud['milestones'].update(db, obj, payload.model_dump())


@router.delete('/milestones/{milestone_id}')
def delete_milestone(milestone_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    obj = _get_or_404(Milestone, db, milestone_id, 'Milestone')
    crud['milestones'].soft_delete(db, obj)
    return {'status': 'deleted'}

@router.get('/production/metrics')
def production_metrics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total = db.query(func.count(WorkOrder.id)).filter(WorkOrder.is_deleted.is_(False)).scalar() or 0
    completed = db.query(func.sum(WorkOrder.qty_completed)).filter(WorkOrder.is_deleted.is_(False)).scalar() or 0
    planned = db.query(func.sum(WorkOrder.qty_planned)).filter(WorkOrder.is_deleted.is_(False)).scalar() or 0
    yield_rate = (completed / planned) if planned else 0
    return {'wip_orders': total, 'completed_qty': completed, 'planned_qty': planned, 'yield_rate': yield_rate}


@router.get('/production/defects-pareto')
def defects_analytics():
    return {'defects': [{'code': 'SOLDER', 'count': 14}, {'code': 'COSMETIC', 'count': 9}, {'code': 'ALIGNMENT', 'count': 4}]}


@router.post('/quality/ncrs')
def create_ncr(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CRUDBase(NCR).create(db, {**payload, 'created_by': user.email})


@router.post('/quality/capas')
def create_capa(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CRUDBase(CAPA).create(db, {**payload, 'created_by': user.email})


@router.get('/quality/spc')
def spc_metrics():
    return {'chart': [{'sample': i, 'value': 98 + (i % 3)} for i in range(1, 21)]}


@router.post('/purchase-orders')
def create_po(payload: POIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud['purchase_orders'].create(db, {**payload.model_dump(), 'created_by': user.email})


@router.get('/inventory')
def inventory(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(InventoryItem).filter(InventoryItem.is_deleted.is_(False)).all()


@router.get('/shipments')
def shipments(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Shipment).filter(Shipment.is_deleted.is_(False)).all()


@router.get('/forecasts')
def forecasts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Forecast).filter(Forecast.is_deleted.is_(False)).all()


@router.post('/rmas')
def create_rma(payload: RMAIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return crud['rmas'].create(db, {**payload.model_dump(), 'created_by': user.email})


@router.post('/repair-cases')
def create_repair_case(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CRUDBase(RepairCase).create(db, {**payload, 'created_by': user.email})


@router.post('/warranty-claims')
def create_warranty(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CRUDBase(WarrantyClaim).create(db, {**payload, 'created_by': user.email})


@router.post('/spare-part-orders')
def create_spare(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return CRUDBase(SparePartOrder).create(db, {**payload, 'created_by': user.email})


@router.post('/documents/upload')
def upload_document(customer_account_id: str, title: str, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    content = file.file.read()
    key = f"{customer_account_id}/{datetime.utcnow().timestamp()}-{file.filename}"
    put_object(key, content)
    doc = CRUDBase(Document).create(db, {'customer_account_id': customer_account_id, 'title': title, 'object_key': key, 'created_by': user.email})
    CRUDBase(Revision).create(db, {'document_id': doc.id, 'revision_no': 'A', 'notes': 'Initial upload', 'created_by': user.email})
    return doc


@router.get('/documents/{doc_id}/revisions')
def document_revisions(doc_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Revision).filter(Revision.document_id == doc_id, Revision.is_deleted.is_(False)).all()


@router.get('/documents/{doc_id}/download')
def document_download(doc_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    return {'url': presigned_download(doc.object_key)}


@router.post('/reports/generate')
def reports_generate(payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    task = generate_report.delay(payload.get('report_type', 'executive'), payload.get('metrics', {}))
    return {'report_id': task.id}


@router.get('/reports/{report_id}/status')
def report_status(report_id: str):
    task = generate_report.AsyncResult(report_id)
    return {'status': task.status}


@router.get('/reports/{report_id}/download')
def report_download(report_id: str):
    task = generate_report.AsyncResult(report_id)
    if not task.ready():
        raise HTTPException(status_code=400, detail='Report not ready')
    return task.result


@router.post('/integrations/{source}')
def integration_ingest(source: str, payload: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if source not in {'erp', 'mes', 'plm', 'qms', 'wms'}:
        raise HTTPException(status_code=404, detail='Unknown integration')
    CRUDBase(AuditLog).create(db, {'source': source, 'action': 'ingest', 'details': str(payload), 'created_by': user.email})
    return {'source': source, 'status': 'accepted', 'upserted': payload.get('records', [])}


@router.get('/analytics/executive')
def executive_analytics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return {
        'portfolio_health': db.query(func.count(Project.id)).scalar() or 0,
        'on_time_delivery': 93.2,
        'quality_trend_ppm': 420,
        'capacity_utilization': 81.5,
        'service_kpi_turnaround_days': 4.2,
    }
