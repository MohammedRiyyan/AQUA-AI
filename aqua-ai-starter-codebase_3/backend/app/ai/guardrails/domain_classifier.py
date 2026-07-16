"""
Domain guardrail: keeps the assistant strictly on hydration/water topics.

Two layers, deliberately kept independent so one bad signal can't let
something through:

  1. Keyword screen — fast, cheap, catches the obvious cases and obvious
     off-topic asks ("write me a poem", "what's the capital of France").
  2. Embedding-similarity screen — compares the question's embedding against
     the centroid of the hydration knowledge base. Catches on-topic-sounding
     but actually-unrelated questions that slip past keywords, and lets
     genuinely hydration-adjacent phrasing through even without a keyword hit.

A question must pass BOTH checks (or score very highly on one) to be treated
as in-domain. Anything that fails gets a fixed, honest refusal rather than a
best-effort answer — this is a hydration coach, not a general chatbot.
"""
from __future__ import annotations

import numpy as np

from app.ai.retrieval.embeddings import embed_query
from app.core.config import get_settings

settings = get_settings()

HYDRATION_KEYWORDS = {
    "water", "hydrat", "dehydrat", "drink", "thirst", "fluid", "electrolyte",
    "sodium", "potassium", "urine", "kidney", "sweat", "coffee", "caffeine",
    "alcohol", "exercise", "workout", "sleep", "skin", "pregnan", "breastfeed",
    "glass", "bottle", "liter", "litre", "ml", "climate", "humidity", "altitude",
    "weight loss", "metabolism", "digestion", "brain", "heart", "blood pressure",
    "who guideline", "cdc", "intake", "daily goal", "container",
}


def keyword_screen(question: str) -> bool:
    q = question.lower()
    return any(kw in q for kw in HYDRATION_KEYWORDS)


def embedding_screen(question: str, domain_centroid: np.ndarray | None) -> float:
    """Cosine similarity (vectors are pre-normalized) between the question and the
    hydration-corpus centroid. Returns 0.0 if no centroid is available yet
    (e.g. before any documents have been ingested)."""
    if domain_centroid is None:
        return 0.0
    q_vec = embed_query(question)
    return float(np.dot(q_vec, domain_centroid))


def is_in_domain(question: str, domain_centroid: np.ndarray | None = None) -> tuple[bool, float]:
    """
    Returns (is_in_domain, confidence). Confidence is a heuristic 0..1 blend
    of both screens, used for the explainability payload — not a substitute
    for a properly calibrated classifier trained on your own labeled data.
    """
    kw_hit = keyword_screen(question)
    sim = embedding_screen(question, domain_centroid)

    if kw_hit and sim >= settings.DOMAIN_SIMILARITY_THRESHOLD:
        return True, min(1.0, 0.6 + sim)
    if kw_hit and domain_centroid is None:
        # No corpus loaded yet — fall back to the keyword screen alone.
        return True, 0.6
    if sim >= settings.DOMAIN_SIMILARITY_THRESHOLD + 0.15:
        return True, min(1.0, 0.5 + sim)
    return False, max(0.0, sim)
