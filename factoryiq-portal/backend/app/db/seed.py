from app.db.session import SessionLocal
from app.models.entities import CustomerAccount, Role, User
from app.models.base import RoleName
from app.core.security import hash_password


def run_seed() -> None:
    db = SessionLocal()
    try:
        customer = db.query(CustomerAccount).filter(CustomerAccount.name == "Demo Customer").first()
        if not customer:
            customer = CustomerAccount(name="Demo Customer", created_by="seed")
            db.add(customer)
            db.commit()
            db.refresh(customer)

        role = db.query(Role).filter(Role.name == RoleName.admin).first()
        if not role:
            role = Role(name=RoleName.admin, created_by="seed")
            db.add(role)
            db.commit()
            db.refresh(role)

        user = db.query(User).filter(User.email == "admin@factoryiq.local").first()
        if not user:
            user = User(
                email="admin@factoryiq.local",
                full_name="Admin User",
                hashed_password=hash_password("admin123"),
                role_id=role.id,
                customer_account_id=customer.id,
                created_by="seed",
            )
            db.add(user)
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
