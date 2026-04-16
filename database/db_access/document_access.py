"""
This module contains functions for accessing and manipulating document data in the database. 
It provides an abstraction layer between the database models and the API routes.
"""

from sqlalchemy.orm import Session
from typing import List
import logging

from database import models
from core.entities import document_entity


logger = logging.getLogger(__name__)


# adds a new document record to the database
def save_document_metadata(
        file_meta_data: document_entity.DocumentCreate, db: Session
) -> document_entity.DocumentRetrieve:
    """
    Saves the document metadata in the database.

    :param file_meta_data: dict containing the document metadata
    :param db: Database session

    :return: DocumentRetrieve entity representing the saved document's metadata
    """
    logger.info(f"Saving document metadata to database for user {file_meta_data.user_id} and file {file_meta_data.file_name}")

    new_doc = models.Document(
        user_id=file_meta_data.user_id,
        file_name=file_meta_data.file_name,
        file_size=file_meta_data.file_size,
        content_type=file_meta_data.content_type,
        r2_key=file_meta_data.r2_key,
        processing_status=models.ProcessingStatus.PROCESSING
    )

    # adding the new document record to the database
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    return document_entity.DocumentRetrieve(
        id=new_doc.id,
        user_id=new_doc.user_id,
        file_name=new_doc.file_name,
        file_size=new_doc.file_size,
        content_type=new_doc.content_type,
        r2_key=new_doc.r2_key,
        created_at=new_doc.created_at,
        processing_status=document_entity.ProcessingStatus(new_doc.processing_status.value)
    )