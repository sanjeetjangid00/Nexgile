import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.entities import Role, User, CustomerAccount
from app.models.base import RoleName
from app.core.security import hash_password


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        db = SessionLocal()
        customer = db.query(CustomerAccount).first() or CustomerAccount(name='Demo Customer', created_by='seed')
        db.add(customer)
        db.commit()
        db.refresh(customer)
        role = db.query(Role).filter(Role.name == RoleName.admin).first() or Role(name=RoleName.admin, created_by='seed')
        db.add(role)
        db.commit()
        db.refresh(role)
        if not db.query(User).filter(User.email == 'admin@factoryiq.local').first():
            user = User(email='admin@factoryiq.local', full_name='Admin User', hashed_password=hash_password('admin123'), role_id=role.id, customer_account_id=customer.id, created_by='seed')
            db.add(user)
            db.commit()
        db.close()
        yield c
