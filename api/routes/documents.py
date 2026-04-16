from fastapi import (
    APIRouter, HTTPException, Depends, Response, status, Body, UploadFile, File
)
from sqlalchemy.orm import Session
from typing import List

from ..schemas import document_schemas
from core.services import document_services
from core.entities import document_entity
from database.database import get_db
from api.routes.auth import get_current_user
from config.settings import settings

import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/docs",
    tags=["Documents"],
)

"""
Need methods for:

- uploading documents
    - get the file, sanitize the file, store the file in r2, store the meta data in the db
- get meta data for a single document
- delete a doc (from the db and from r2)
"""

"""
Endpoints for document management
"""


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a document, sanitizes it, stores it in R2, and saves the metadata in the database.

    :return: A success message or the created document's metadata
    """
    logger.info(f"Received request to upload document")

    # allowing only pdf files for now, can add more types later
    if file.content_type != "application/pdf":
        logger.warning(f"Unsupported file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # checking size cap of 10 MB
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:
        logger.warning(f"File size exceeds limit: {len(file_bytes)} bytes")
        raise HTTPException(status_code=400, detail="File size exceeds 10 MB limit")

    # creating document entity
    doc_upload: document_entity.DocumentUpload = document_entity.DocumentUpload(
        user_id=user["id"],
        file_name=file.filename,
        file_size=len(file_bytes),
        content_type=file.content_type,
        file_bytes=file_bytes
    )

    # uploading file to R2
    # meta data is returned if upload is successful, otherwise an exception is raised
    file_meta_data = document_services.upload_document(doc_upload, db)

    # convert it to a schema and return
    document_schema = document_schemas.DocumentCreate(
        user_id=file_meta_data["user_id"],
        file_name=file_meta_data["file_name"],
        file_size=file_meta_data["file_size"],
        content_type=file_meta_data["content_type"],
    )
    return document_schema
