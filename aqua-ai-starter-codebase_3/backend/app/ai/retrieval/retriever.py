from app.ai.retrieval.embeddings import embed_query
from app.ai.retrieval.vector_store import VectorHit, get_vector_store
from app.core.config import get_settings

settings = get_settings()


def retrieve(query: str, top_k: int | None = None) -> list[VectorHit]:
    """Semantic search over the hydration knowledge base. Returns ranked passages with scores."""
    store = get_vector_store()
    query_vector = embed_query(query)
    return store.search(query_vector, top_k or settings.RETRIEVAL_TOP_K)
