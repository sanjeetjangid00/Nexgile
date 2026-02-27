from fastapi import FastAPI
from app.api.routes import router
from app.db.base import Base
from app.db.session import engine
import app.models  # noqa

app = FastAPI(title="FactoryIQ Portal")
app.include_router(router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
