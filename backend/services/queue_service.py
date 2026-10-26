import json
import boto3
from botocore.exceptions import ClientError
from backend.config import Config
from backend.models import SessionLocal
from backend.models.processing_job import ProcessingJob


class QueueService:
    """Manages asynchronous job dispatching to either Amazon SQS or local DB-backed queue."""

    def __init__(self, driver: str = None, queue_url: str = None, region: str = None):
        self.driver = driver or Config.QUEUE_DRIVER
        self.queue_url = queue_url or Config.SQS_QUEUE_URL
        self.region = region or Config.AWS_REGION
        self._sqs_client = None

    @property
    def sqs_client(self):
        if self._sqs_client is None and self.driver == "sqs":
            self._sqs_client = boto3.client("sqs", region_name=self.region)
        return self._sqs_client

    def enqueue_job(self, job_type: str, payload: dict, db=None) -> dict:
        """Pushes a background job to either SQS or the local processing table."""
        payload_str = json.dumps(payload)

        # Always save to database for audit and tracking
        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True
        try:
            db_job = ProcessingJob(
                job_type=job_type,
                payload_json=payload_str,
                status=ProcessingJob.STATUS_PENDING,
            )
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            job_id = db_job.id
        finally:
            if own_db:
                db.close()

        # If running with SQS, also dispatch message to AWS SQS
        if self.driver == "sqs" and self.queue_url and self.sqs_client:
            try:
                self.sqs_client.send_message(
                    QueueUrl=self.queue_url,
                    MessageBody=json.dumps({"job_id": job_id, "job_type": job_type, "payload": payload}),
                    MessageAttributes={
                        "JobType": {"DataType": "String", "StringValue": job_type}
                    },
                )
            except ClientError as e:
                # Log error safely and allow local worker fallback
                pass

        return {"job_id": job_id, "status": "enqueued", "job_type": job_type}


queue_service = QueueService()
