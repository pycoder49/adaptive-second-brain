"""
RAG Pipeline — Retrieval-Augmented Generation

Flow:
1. Document upload → parse PDF/DOCX → chunk text → embed locally (sentence-transformers) → store in pgvector
2. User query → embed query locally → pgvector similarity search → send context + query to OpenAI → return answer

Embeddings: all-MiniLM-L6-v2 (384 dimensions, runs locally, free)
LLM: OpenAI (hardcoded for now via OPENAI_API_KEY in .env)
Vector DB: pgvector on Aiven PostgreSQL
"""
import logging
from pathlib import Path
from typing import List
import io

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from sqlalchemy.orm import Session

from config.settings import settings
from database.db_access import document_access, chunk_access
from database import models


logger = logging.getLogger(__name__)

# Embedding Model (loaded once, reused) 384 dimensions, fast, good quality for RAG
_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    """Lazy-load the embedding model (only loaded once)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model



def parse_pdf(file_bytes: bytes) -> str:
    text = ""
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def parse_docx(file_bytes: bytes) -> str:

    doc = DocxDocument(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def parse_file(filename: str, file_bytes: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return parse_pdf(file_bytes)
    elif ext in (".docx", ".doc"):
        return parse_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Supported: .pdf, .docx")



def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return splitter.split_text(text)




def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    model = get_embedding_model()
    embedding = model.encode(query)
    return embedding.tolist()



def ingest_document(user_id: int, filename: str, file_bytes: bytes, db: Session) -> models.Document:

    doc = document_access.create_document(user_id, filename, db)
    logger.info(f"Created document record: id={doc.id}, filename={filename}")

    try:
        logger.info(f"Parsing {filename}...")
        text = parse_file(filename, file_bytes)
        if not text.strip():
            raise ValueError(f"No text could be extracted from {filename}")

        logger.info(f"Chunking text ({len(text)} chars)...")
        chunks = chunk_text(text)
        logger.info(f"Created {len(chunks)} chunks")

        logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        embeddings = embed_texts(chunks)

        chunk_data = [
            {"content": content, "embedding": embedding}
            for content, embedding in zip(chunks, embeddings)
        ]
        chunk_access.store_chunks(doc.id, chunk_data, db)
        logger.info(f"Stored {len(chunk_data)} chunks in pgvector")

        document_access.update_document_status(doc.id, models.ProcessingStatus.READY, db)
        logger.info(f"Document {doc.id} ingestion complete")

    except Exception as e:
        logger.error(f"Document ingestion failed for {filename}: {e}")
        document_access.update_document_status(doc.id, models.ProcessingStatus.FAILED, db)
        raise


    db.refresh(doc)
    return doc


##RAG QUERY 

def query_rag(
    user_query: str,
    document_ids: List[int],
    db: Session,
    top_k: int = 10,
) -> str:
    logger.info(f"Embedding query: {user_query[:80]}...")
    query_emb = embed_query(user_query)

    results = chunk_access.search_similar_chunks(query_emb, document_ids, db, top_k=top_k)

    if not results:
        return "I couldn't find any relevant information in the uploaded documents to answer your question."

    context_parts = []
    for chunk, distance in results:
        doc = document_access.get_document_by_id(chunk.document_id, db)
        source = doc.filename if doc else "Unknown"
        context_parts.append(f"[Source: {source}]\n{chunk.content}")

    context = "\n\n---\n\n".join(context_parts)

    logger.info(f"Calling OpenAI with {len(results)} context chunks...")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    system_prompt = (
        "You are a helpful assistant that answers questions based ONLY on the provided document context. "
        "If the context doesn't contain enough information to answer the question, say so honestly. "
        "Do not make up information or use knowledge outside the provided context. "
        "Cite the source document when possible."
    )

    user_prompt = f"Context from uploaded documents:\n\n{context}\n\n---\n\nQuestion: {user_query}\n\nAnswer:"

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    answer = response.choices[0].message.content
    logger.info("RAG query complete")
    return answer



