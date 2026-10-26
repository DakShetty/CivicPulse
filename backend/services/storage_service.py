import os
import uuid
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
from backend.config import Config


class StorageService:
    """Manages file storage with support for local disk and private Amazon S3 with pre-signed URLs."""

    def __init__(self, driver: str = None, bucket_name: str = None, region: str = None):
        self.driver = driver or Config.STORAGE_DRIVER
        self.bucket_name = bucket_name or Config.S3_BUCKET_NAME
        self.region = region or Config.AWS_REGION
        self.local_dir = Path(Config.LOCAL_STORAGE_DIR)
        
        # Ensure local directory exists
        self.local_dir.mkdir(parents=True, exist_ok=True)
        (self.local_dir / "attachments").mkdir(exist_ok=True)
        (self.local_dir / "reports").mkdir(exist_ok=True)

        self._s3_client = None

    @property
    def s3_client(self):
        if self._s3_client is None and self.driver == "s3":
            self._s3_client = boto3.client("s3", region_name=self.region)
        return self._s3_client

    def save_file(self, file_bytes: bytes, original_filename: str, prefix: str = "attachments") -> tuple[str, int]:
        """Saves file bytes to either local storage or private S3.
        Returns: (object_key, file_size_bytes)
        """
        ext = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "bin"
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        object_key = f"{prefix}/{unique_name}"
        file_size = len(file_bytes)

        if self.driver == "s3":
            try:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=file_bytes,
                    ServerSideEncryption="AES256",
                )
            except ClientError as e:
                # If S3 fails or is not accessible, fallback safely to local disk
                fallback_path = self.local_dir / object_key
                fallback_path.parent.mkdir(parents=True, exist_ok=True)
                with open(fallback_path, "wb") as f:
                    f.write(file_bytes)
                return object_key, file_size
        else:
            local_path = self.local_dir / object_key
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(file_bytes)

        return object_key, file_size

    def generate_download_url(self, object_key: str, expires_in_seconds: int = 3600) -> str:
        """Generates an authorized short-lived download URL.
        For S3: returns an authenticated pre-signed URL.
        For local: returns local API serving endpoint URL.
        """
        if self.driver == "s3" and self.s3_client:
            try:
                url = self.s3_client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.bucket_name, "Key": object_key},
                    ExpiresIn=expires_in_seconds,
                )
                return url
            except Exception:
                pass
        
        # Local serving endpoint
        return f"/api/v1/storage/download/{object_key}"

    def get_local_path(self, object_key: str) -> Path | None:
        """Returns local filesystem path if file exists locally."""
        path = self.local_dir / object_key
        return path if path.exists() else None


# Default singleton instance
storage_service = StorageService()
