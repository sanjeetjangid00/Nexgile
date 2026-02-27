.PHONY: install test seed run-backend run-frontend

install:
	pip install -r requirements.txt

test:
	cd backend && PYTHONPATH=. pytest tests -q

seed:
	cd backend && PYTHONPATH=. python app/db/seed.py

run-backend:
	cd backend && PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	streamlit run frontend_streamlit/app.py --server.port 8501 --server.address 0.0.0.0
