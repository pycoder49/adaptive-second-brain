from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import logging

from ..schemas import document_schemas
from core.services import document_services

from database.database import get_db
from api.routes.auth import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post("/upload", response_model=document_schemas.DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    allowed_extensions = (".pdf", ".docx", ".doc")
    if not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    logger.info(f"Uploading document '{file.filename}' for user {user['id']}")

    file_bytes = await file.read()

    try:
        result = document_services.upload_document(user["id"], file.filename, file_bytes, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    return result


@router.get("/", response_model=List[document_schemas.DocumentResponse])
def get_documents(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    return document_services.get_user_documents(user["id"], db)


@router.delete("/{doc_id}")
def delete_document(
    doc_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    deleted = document_services.delete_user_document(user["id"], doc_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found or unauthorized")
    return {"detail": "Document deleted successfully"}