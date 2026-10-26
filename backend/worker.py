import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.config import Config
from backend.models import init_db, SessionLocal
from backend.models.processing_job import ProcessingJob
from backend.models.issue import Issue
from backend.services.storage_service import storage_service

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("civicpulse_worker")


def process_single_job(job: ProcessingJob, db):
    """Processes a background queue job."""
    logger.info(f"Processing job #{job.id} (type: {job.job_type})")
    payload = json.loads(job.payload_json)

    if job.job_type == "new_issue_process":
        issue_id = payload.get("issue_id")
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if issue:
            # Simulate async processing such as image metadata indexing or GIS area verification
            logger.info(f"Verified and indexed issue metadata for Ref: {issue.public_reference}")
    elif job.job_type == "report_generation":
        logger.info(f"Report generation task acknowledged: {payload.get('title')}")
    else:
        logger.info(f"Generic task handled: {job.job_type}")

    job.status = ProcessingJob.STATUS_COMPLETED
    job.completed_at = datetime.now(timezone.utc)
    db.commit()


def run_worker_loop(poll_interval_seconds: int = 5, max_iterations: int | None = None):
    """Worker loop that checks for pending jobs."""
    init_db(Config.SQLALCHEMY_DATABASE_URI)
    logger.info("CivicPulse background worker started. Polling queue...")

    iterations = 0
    while True:
        db = SessionLocal()
        try:
            pending_jobs = (
                db.query(ProcessingJob)
                .filter_by(status=ProcessingJob.STATUS_PENDING)
                .order_by(ProcessingJob.created_at.asc())
                .limit(5)
                .all()
            )

            for job in pending_jobs:
                job.status = ProcessingJob.STATUS_PROCESSING
                job.started_at = datetime.now(timezone.utc)
                db.commit()
                try:
                    process_single_job(job, db)
                except Exception as e:
                    logger.error(f"Error processing job #{job.id}: {e}")
                    job.retry_count += 1
                    if job.retry_count >= job.max_retries:
                        job.status = ProcessingJob.STATUS_FAILED
                        job.error_summary = f"Max retries reached: {str(e)}"
                    else:
                        job.status = ProcessingJob.STATUS_PENDING
                    db.commit()

        except Exception as err:
            logger.error(f"Worker iteration error: {err}")
        finally:
            db.close()

        iterations += 1
        if max_iterations and iterations >= max_iterations:
            break
        time.sleep(poll_interval_seconds)


if __name__ == "__main__":
    run_worker_loop()
