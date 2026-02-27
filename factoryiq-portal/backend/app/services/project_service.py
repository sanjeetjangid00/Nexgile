from app.models.entities import Milestone


def calculate_project_health(db, project_id: str) -> str:
    milestones = db.query(Milestone).filter(Milestone.project_id == project_id, Milestone.is_deleted.is_(False)).all()
    if not milestones:
        return "Green"
    delayed = sum(1 for m in milestones if m.actual_date and m.actual_date > m.planned_date)
    ratio = delayed / len(milestones)
    if ratio > 0.5:
        return "Red"
    if ratio > 0.2:
        return "Yellow"
    return "Green"
