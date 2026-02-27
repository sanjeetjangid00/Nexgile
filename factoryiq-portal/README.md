# Nexgile – FactoryIQ Manufacturing Excellence Portal

## Architecture Overview
FactoryIQ is a modular MVP using FastAPI backend services, SQLAlchemy ORM entities, JWT auth with RBAC, Redis/Celery async workers, MinIO S3-compatible document storage, and a Streamlit analytics front-end.

## Modules Delivered
- Program/Project/Milestone management with health scoring and delay alerts.
- Production visibility APIs (WIP, yield, defect Pareto).
- Quality APIs (NCR, CAPA, SPC, audits).
- Supply chain APIs (PO, inventory, shipments, forecasts).
- After-sales APIs (RMA, repair, warranty, spare parts, EOL).
- Document upload/download with revisions via MinIO.
- Reporting engine through Celery async task APIs.
- Integration ingest endpoints for ERP/MES/PLM/QMS/WMS with audit logging.

## Project Layout
```text
factoryiq-portal/
├── backend/
├── frontend_streamlit/
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

## Local Setup (No Docker)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create environment file:
   ```bash
   cp .env.example .env
   ```
3. `.env.example` is already minimal for local SQLite. Keep as-is unless you need external services.
4. Seed demo user:
   ```bash
   cd backend
   PYTHONPATH=. python app/db/seed.py
   ```
5. Start backend API:
   ```bash
   cd backend
   PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
6. Start Streamlit UI in a second terminal:
   ```bash
   streamlit run frontend_streamlit/app.py --server.port 8501 --server.address 0.0.0.0
   ```
7. Access services:
   - API: http://localhost:8000/docs
   - Streamlit: http://localhost:8501


## Required `.env` Keys (No Docker)
Only these keys are required for the local non-Docker workflow:
- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `SMTP_FROM`

Everything else (Redis/MinIO/Postgres overrides) is optional and can stay commented in `.env.example`.

## Optional Services for Full Feature Set
- Redis + Celery are required for async report task execution.
- MinIO/S3-compatible storage is required for document upload/download endpoints.
- PostgreSQL is recommended for production-like testing.

## Local Test Run
```bash
pip install -r requirements.txt
cd backend
PYTHONPATH=. pytest tests -q
```

## Example Credentials
- Email: `admin@factoryiq.local`
- Password: `admin123`

## Integration Example Payloads
- `POST /integrations/erp`
```json
{"records": [{"entity": "PurchaseOrder", "po_number": "PO-1001"}]}
```
- `POST /integrations/mes`
```json
{"records": [{"entity": "WorkOrder", "code": "WO-1001", "qty_completed": 40}]}
```
- `POST /integrations/plm`
```json
{"records": [{"entity": "BOM", "project": "Alpha", "version": "B"}]}
```
- `POST /integrations/qms`
```json
{"records": [{"entity": "NCR", "title": "Scratch defect"}]}
```
- `POST /integrations/wms`
```json
{"records": [{"entity": "InventoryItem", "sku": "P-445", "quantity": 800}]}
```

## Notes
- Alembic folder is scaffolded; create formal migration revisions before production rollout.
- UUID foreign key columns are aligned with UUID primary keys for PostgreSQL compatibility.
- `GET /rmas` endpoint is available for After-Sales page loading.

## Troubleshooting
- If FastAPI cannot find `.env`, run commands from `factoryiq-portal/` root or export vars in shell before startup.
- If reports stay pending, ensure Redis is available and Celery worker is running.
- If document upload fails, ensure MinIO/S3 variables are set and the bucket exists.
