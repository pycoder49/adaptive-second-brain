"""
RAG factory -> returns the correct RAG implementation based on the

*****RAG_IMPLEMENTATION setting in .env*****

Values:
    "placeholder"  → PlaceholderRAG  (safe default, no real logic)
    "dev"          → DevRAG          (Aryan's personal dev implementation)
    "production"   → ProductionRAG   (Production-ready implementation owned by Renee)
"""
from core.RAG.rag_interface import RAGInterface
from config.settings import settings


def get_rag_engine() -> RAGInterface:
    impl = settings.RAG_IMPLEMENTATION.lower()

    if impl == "dev":
        from core.RAG.implementations.dev_rag import DevRAG
        return DevRAG()

    if impl == "production":
        from core.RAG.implementations.production_rag import ProductionRAG
        return ProductionRAG()

    # default fallback
    from core.RAG.implementations.placeholder_rag import PlaceholderRAG
    return PlaceholderRAG()
