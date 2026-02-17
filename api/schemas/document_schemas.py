
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    upload_date: str
    processing_status: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
