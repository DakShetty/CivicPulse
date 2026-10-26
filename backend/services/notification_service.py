import boto3
from botocore.exceptions import ClientError
from backend.config import Config
from backend.models import SessionLocal
from backend.models.issue import NotificationEvent


class NotificationService:
    """Manages civic notifications with in-app event tracking and optional Amazon SNS integration."""

    def __init__(self, driver: str = None, topic_arn: str = None, region: str = None):
        self.driver = driver or Config.NOTIFICATION_DRIVER
        self.topic_arn = topic_arn or Config.SNS_TOPIC_ARN
        self.region = region or Config.AWS_REGION
        self._sns_client = None

    @property
    def sns_client(self):
        if self._sns_client is None and self.driver == "sns":
            self._sns_client = boto3.client("sns", region_name=self.region)
        return self._sns_client

    def send_notification(
        self,
        subject: str,
        body: str,
        issue_id: int | None = None,
        recipient: str | None = None,
        channel: str = "in_app",
        db=None,
    ) -> dict:
        """Dispatches notification and logs event in DB."""
        status = "sent"
        error_summary = None

        if self.driver == "sns" and self.topic_arn and self.sns_client:
            try:
                self.sns_client.publish(
                    TopicArn=self.topic_arn,
                    Subject=subject[:100],
                    Message=body,
                )
                channel = "sns"
            except ClientError as e:
                status = "failed"
                error_summary = f"SNS publish failed: {str(e)}"
        elif channel == "email":
            # In local mode, simulate delivery
            status = "simulated"

        own_db = False
        if db is None:
            db = SessionLocal()
            own_db = True
        try:
            event = NotificationEvent(
                issue_id=issue_id,
                channel=channel,
                recipient=recipient or "staff@civicpulse.local",
                subject=subject,
                body=body,
                status=status,
                error_summary=error_summary,
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            event_id = event.id
        finally:
            if own_db:
                db.close()

        return {"event_id": event_id, "status": status, "channel": channel}


notification_service = NotificationService()
