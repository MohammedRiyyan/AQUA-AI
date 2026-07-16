"""
Local embedding model wrapper.

Uses sentence-transformers running on-device/on-server — no network call to
any hosted embeddings API. Swap EMBEDDING_MODEL in core/config.py for your
own fine-tuned bi-encoder once you've trained one on hydration-domain text
pairs (e.g. question <-> supporting-passage pairs mined from your corpus).
"""
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedder()
    return model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)


def embed_query(text: str) -> np.ndarray:
    return embed_texts([text])[0]
