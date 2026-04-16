from sqlalchemy.orm import Session
from typing import List
import logging

from database.db_access import document_access
from core.entities import document_entity

from config.settings import settings
from config.r2_client import s3_client



logger = logging.getLogger(__name__)


# upload the document to R2 bucket
def upload_document(document: document_entity.DocumentUpload, db: Session) -> dict:
    """
    Uploads a document to R2 storage and saves the metadata in the database.

    :param document: DocumentUpload entity containing the document details
    :param db: Database session

    :return: dict representing the uploaded document's metadata
    """

    # using the s3 client to upload the file to R2
    logger.info(f"Uploading document to R2: {document.file_name} for user {document.user_id}")

    r2_key = f"{document.user_id}/{document.file_name}"
    try:
        s3_client.put_object(
            Bucket=settings.BUCKET_NAME,
            Key=r2_key,
            Body=document.file_bytes,
            ContentType=document.content_type,
        )
    except Exception as e:
        logger.error(f"Error uploading document to R2: {e}")
        raise Exception("Failed to upload document to R2")
    
    # now saving doc metadata in the database
    document_meta_data = document_entity.DocumentCreate(
        user_id=document.user_id,
        file_name=document.file_name,
        file_size=document.file_size,
        content_type=document.content_type,
        r2_key=r2_key
    )
    result = document_access.save_document_metadata(document_meta_data, db)

    return {
        "user_id": result.user_id,
        "file_name": result.file_name,
        "file_size": result.file_size,
        "content_type": result.content_type,
    }
