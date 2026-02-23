"""
Development RAG implementation — Aryan's personal RAG pipeline.
Set RAG_IMPLEMENTATION=dev in your .env to use this.
"""
from core.RAG.rag_interface import RAGInterface


class DevRAG(RAGInterface):

    def get_response(self, user_id: int, query: str) -> str:
        # TODO: implement your RAG pipeline here
        # Steps: Roughly for now -- more on the details later
        # 1. Embed the query
        # 2. Run pgvector similarity search scoped to user_id
        # 3. Build context from retrieved chunks
        # 4. Call LLM with context + query
        # 5. Return the response string
        raise NotImplementedError("DevRAG.get_response() is not yet implemented")
