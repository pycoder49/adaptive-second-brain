"""
Abstract interface for RAG implementations.
All RAG implementations must inherit from this class.
"""
from abc import ABC, abstractmethod


class RAGInterface(ABC):

    @abstractmethod
    def get_response(self, user_id: int, query: str) -> str:
        """
        Given a user query, retrieve relevant chunks and generate a response.

        :param user_id: The ID of the user making the query (used to scope document retrieval)
        :param query: The user's question or prompt
        :return: The generated response string
        """
        pass
