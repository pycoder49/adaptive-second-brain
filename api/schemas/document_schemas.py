from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# document metadata schema for response after upload
class DocumentCreate(BaseModel):
    user_id: int
    file_name: str
    file_size: int
    content_type: str
