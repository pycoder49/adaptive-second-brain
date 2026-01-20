from sqlalchemy.orm import Session
from typing import List
import datetime
import logging

from api.schemas import chat_schemas


logger = logging.getLogger(__name__)


def get_all_conversations(db: Session) -> List[chat_schemas.Chat]:
    

def get_all_messages(db: Session, chat_id)