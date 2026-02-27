from app.models.entities import Notification


def notify(db, message: str, user_id: str | None = None, created_by: str = "system"):
    obj = Notification(message=message, user_id=user_id, created_by=created_by)
    db.add(obj)
    db.commit()
    return obj


def send_email_stub(to_email: str, subject: str, body: str) -> dict:
    return {"to": to_email, "subject": subject, "body": body, "status": "queued_stub"}
