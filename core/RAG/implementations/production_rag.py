"""
Production RAG implementation — owned by the Renee.
Set RAG_IMPLEMENTATION=production in your .env to use this.
"""
from core.RAG.rag_interface import RAGInterface


class ProductionRAG(RAGInterface):

    def get_response(self, user_id: int, query: str) -> str:
        # TODO: RAG team implements this
        raise NotImplementedError("ProductionRAG.get_response() is not yet implemented")
