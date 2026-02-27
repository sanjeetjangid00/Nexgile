from sqlalchemy import select


class CRUDBase:
    def __init__(self, model):
        self.model = model

    def create(self, db, obj_in: dict):
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def get(self, db, obj_id):
        return db.get(self.model, obj_id)

    def list(self, db, skip=0, limit=50, filters=None):
        stmt = select(self.model).where(self.model.is_deleted.is_(False))
        for key, value in (filters or {}).items():
            if value is not None and hasattr(self.model, key):
                stmt = stmt.where(getattr(self.model, key) == value)
        return db.execute(stmt.offset(skip).limit(limit)).scalars().all()

    def update(self, db, obj, data: dict):
        for k, v in data.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        return obj

    def soft_delete(self, db, obj):
        obj.is_deleted = True
        db.commit()
        return obj
