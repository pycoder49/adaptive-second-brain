# Adaptive AI Second Brain

A full-stack intelligent knowledge management platform that lets you chat with your documents using RAG (Retrieval-Augmented Generation). Upload PDFs, ask questions, and get AI-powered answers from your personal knowledge base.

## Overview

This project goes beyond simple document search by tracking how you engage with your knowledge base and surfacing your most-referenced topics on a personalized dashboard. It's designed for students, researchers, and knowledge workers who want to make their documents searchable and conversational.

## Features

### MVP (Current Scope)
- **Document Upload**: Upload PDF documents to your personal knowledge base
- **RAG-Powered Chat**: Ask questions and get answers grounded in your documents
- **Smart Retrieval**: Vector similarity search finds the most relevant content
- **Usage Analytics**: Track which documents you reference most frequently
- **Personalized Dashboard**: See your top 5 most-retrieved documents on login
- **User Authentication**: Secure email/password authentication

### Future Enhancements
- Multiple file format support (DOCX, TXT, Markdown)
- OAuth authentication
- Advanced retrieval strategies (re-ranking, hybrid search)
- Spaced repetition suggestions for learning
- Document tagging and organization

## Architecture

### Tech Stack
- **Frontend**: Streamlit (MVP) → React (later)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL with pgvector extension
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **LLM**: OpenAI GPT-4 / Anthropic Claude
- **Task Queue**: Redis (for async document processing)

### High-Level Flow
```
User uploads PDF →
  Extract text → Chunk into segments → Generate embeddings →
  Store in vector database

User asks question →
  Embed question → Search similar chunks → Send to LLM →
  Return contextualized answer → Log query (async)

Dashboard loads →
  Aggregate most-retrieved documents from past 7 days →
  Display top 5 with retrieval counts
```

## Project Structure

```
second-brain/
├── api/              # FastAPI routes and endpoints
├── core/             # RAG logic (chunking, embedding, retrieval, LLM)
├── database/         # SQLAlchemy models and migrations
├── config/           # YAML configs for tunable parameters
├── frontend/         # Streamlit UI
└── tests/            # Unit tests and evaluation framework
```

## Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 15+ with pgvector extension
- Redis (optional, for background tasks)
- OpenAI API key or Anthropic API key

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/second-brain.git
cd second-brain
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL with pgvector
```bash
# Install pgvector extension
CREATE EXTENSION vector;
```

5. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your settings:
# - DATABASE_URL
# - OPENAI_API_KEY or ANTHROPIC_API_KEY
# - SECRET_KEY for JWT
```

6. Run database migrations
```bash
alembic upgrade head
```

7. Start the API server
```bash
uvicorn api.main:app --reload
```

8. Start the frontend (in a new terminal)
```bash
streamlit run frontend/app.py
```

## Configuration

All tunable parameters are in `config/` directory:

### `config/chunking.yaml`
```yaml
chunk_size: 512        # tokens per chunk
overlap: 50            # token overlap between chunks
min_chunk_length: 100  # minimum chunk size
```

### `config/retrieval.yaml`
```yaml
top_k: 5                    # number of chunks to retrieve
min_similarity: 0.3         # minimum similarity threshold
```

### `config/prompts.yaml`
Contains system prompts and RAG templates for the LLM.

**To experiment**: Just change values in YAML files and restart the server. No code changes needed.

## Database Schema

```sql
users
  - id, email, password_hash

documents
  - id, user_id, filename, upload_date, processing_status

chunks
  - id, document_id, content, embedding (vector), chunk_index

query_logs
  - id, user_id, query, retrieved_chunk_ids, timestamp, latency_ms, user_feedback
```

## Development Workflow

### Adding a New Document
1. User uploads PDF via frontend
2. API stores file and creates `Document` record with status "processing"
3. Background task:
   - Extracts text from PDF
   - Chunks text based on config
   - Generates embeddings in batch
   - Stores chunks with vectors in DB
   - Updates document status to "ready"

### Handling a Query
1. User submits question
2. Embed question using same model
3. Vector similarity search for top-k chunks
4. Build context from retrieved chunks
5. Send context + question to LLM
6. Return answer to user
7. Async: Log query and retrieved chunks

### Viewing Dashboard
1. Query aggregates `query_logs` from past 7 days
2. Groups by document, counts retrievals
3. Returns top 5 documents
4. Frontend displays with retrieval counts

## Evaluation Framework

Located in `tests/evaluation/`:

### Test Cases Structure
```json
{
  "question": "What are the main components of RAG?",
  "expected_chunks": ["chunk_id_123"],
  "expected_answer_contains": ["retrieval", "generation"],
  "difficulty": "easy"
}
```

### Metrics Tracked for MVP
- **Retrieval Accuracy**: Precision@k, Recall@k
- **Answer Quality**: LLM-based evaluation or manual review
- **End-to-End Latency**: Time from query to response
- **Cost per Query**: API costs for embeddings + LLM

### Running Evaluation
```bash
python tests/evaluation/run_evaluation.py
```

## Performance Considerations

### Speed Optimizations
- **Async document processing**: User doesn't wait for chunking/embedding
- **Batch embedding**: Process 32+ chunks in one API call
- **Indexed vector search**: pgvector with proper indexing keeps search <300ms
- **Async logging**: Query logging doesn't block user response

### Cost Management
- Self-hosted embedding model (free) vs OpenAI embeddings ($0.00002/1K tokens)
- Claude Haiku (~$0.003/query) vs GPT-4 (~$0.015/query)
- Estimated: $3-15/month for 1000 queries

### Scalability Path
1. **Single server** (MVP) → handles 100s of users
2. **Add load balancer** → multiple API servers for 1000s of users
3. **Migrate to Qdrant/Weaviate** → if vector search becomes bottleneck
4. **Add caching layer** → Redis for frequently asked questions


## Key Design Decisions

### Why pgvector over Pinecone/Weaviate?
- Simpler architecture (one database vs two systems)
- Easier to join user data with vectors
- Sufficient for <100K documents
- Lower operational complexity

### Why fixed-size chunking?
- Simple, predictable, fast
- Semantic chunking can be added later if needed
- Easy to reason about and debug

### Why async document processing?
- User gets immediate feedback ("processing...")
- Can upload multiple documents without waiting
- Scales better under load

### Why separate config files?
- Easy experimentation (change chunk_size without touching code)
- Version control configuration alongside code
- Clear documentation of current settings
