
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Tuple
import logging

from database import models


logger = logging.getLogger(__name__)


def store_chunks(document_id: int, chunks: List[dict], db: Session) -> List[models.Chunk]:

    logger.info(f"Storing {len(chunks)} chunks for document {document_id}")
    chunk_objects = []
    for chunk_data in chunks:
        chunk = models.Chunk(
            document_id=document_id,
            content=chunk_data["content"],
            embedding=chunk_data["embedding"],
        )
        db.add(chunk)
        chunk_objects.append(chunk)

    db.commit()
    for c in chunk_objects:
        db.refresh(c)

    return chunk_objects


def search_similar_chunks(
    query_embedding: List[float],
    document_ids: List[int],
    db: Session,
    top_k: int = 10,
) -> List[Tuple[models.Chunk, float]]:

    if not document_ids:
        logger.warning("No document IDs provided for similarity search")
        return []

    logger.info(f"Searching top {top_k} similar chunks across {len(document_ids)} documents")

 
    embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

    results = (
        db.query(models.Chunk, models.Chunk.embedding.cosine_distance(query_embedding).label("distance"))
        .filter(models.Chunk.document_id.in_(document_ids))
        .order_by("distance")
        .limit(top_k)
        .all()
    )

    return results


def get_chunks_for_document(document_id: int, db: Session) -> List[models.Chunk]:

    return (
        db.query(models.Chunk)
        .filter(models.Chunk.document_id == document_id)
        .all()
    )


def delete_chunks_for_document(document_id: int, db: Session) -> int:

    count = db.query(models.Chunk).filter(models.Chunk.document_id == document_id).delete()
    db.commit()
    return count
