import uuid
from datetime import datetime

from pydantic import BaseModel


class SourceCitation(BaseModel):
    title: str
    document_id: str | None = None
    relevance_score: float


class AIAnswer(BaseModel):
    """
    Standard explainable-AI response shape returned by every endpoint that
    calls the custom hydration model — daily advice, reminders, and chat.
    """
    text: str
    confidence: float                     # 0..1
    reasoning: str                        # short natural-language rationale
    sources: list[SourceCitation] = []
    model_version: str | None = None
    is_in_domain: bool = True             # false when the guardrail rejected an off-topic question


class ChatRequest(BaseModel):
    question: str


class AIRecommendationOut(BaseModel):
    id: uuid.UUID
    kind: str
    output_text: str
    confidence: float
    reasoning: str | None
    retrieved_sources: list
    created_at: datetime

    class Config:
        from_attributes = True
