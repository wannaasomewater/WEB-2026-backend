import uuid
import boto3
from botocore.client import Config
from core.config import settings


class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=f"http://{settings.S3_ENDPOINT}",
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        self.bucket = settings.S3_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except Exception:
            try:
                self.client.create_bucket(Bucket=self.bucket)
                print(f"Бакет {self.bucket} создан")
            except Exception as e:
                print(f"Не удалось создать бакет: {e}")

    async def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket,
            Key=file_name,
            Body=file_content,
            ContentType=content_type,
        )
        return f"http://{settings.S3_ENDPOINT}/{self.bucket}/{file_name}"

    @staticmethod
    def generate_file_name(original_name: str, appliance_id: int, file_type: str) -> str:
        ext = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else "bin"
        unique = uuid.uuid4().hex[:8]
        return f"{file_type}_{appliance_id}_{unique}.{ext}"


s3_service = S3Service()
