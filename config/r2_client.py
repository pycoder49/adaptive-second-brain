import boto3
from config.settings import settings


s3_client = boto3.client(
    "s3",
    endpoint_url = settings.S3_ENDPOINT_URL,
    aws_access_key_id = settings.ACCOUNT_KEY_ID,
    aws_secret_access_key = settings.SECRET_ACCESS_KEY,
    region_name = "us-east-1",
)