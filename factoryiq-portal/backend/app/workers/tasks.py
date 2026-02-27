import csv
from io import StringIO
from app.workers.celery_app import celery_app


@celery_app.task(name="generate_report")
def generate_report(report_type: str, payload: dict):
    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["metric", "value"])
    for k, v in payload.items():
        writer.writerow([k, v])
    return {"report_type": report_type, "format": "csv", "content": stream.getvalue()}
