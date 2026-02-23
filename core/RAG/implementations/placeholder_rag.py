"""
Placeholder RAG implementation — returns a hardcoded string.
Used as a safe fallback during development.
"""
from core.RAG.rag_interface import RAGInterface


class PlaceholderRAG(RAGInterface):

    def get_response(self, user_id: int, query: str) -> str:
        return "This is a placeholder response. No RAG implementation is active."
