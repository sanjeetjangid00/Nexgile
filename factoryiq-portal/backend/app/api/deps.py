from fastapi import Depends, HTTPException, status
import uuid
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import User, RoleName

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = uuid.UUID(payload.get("sub"))
    except (JWTError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def enforce_roles(*allowed: RoleName):
    def checker(user=Depends(get_current_user)):
        role = user.role.name if hasattr(user, "role") and user.role else None
        if role not in allowed and role != RoleName.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return user
    return checker


def customer_scope_filter(user, model, stmt):
    if user.role and user.role.name == RoleName.admin:
        return stmt
    if hasattr(model, "customer_account_id") and user.customer_account_id:
        return stmt.where(model.customer_account_id == user.customer_account_id)
    return stmt
