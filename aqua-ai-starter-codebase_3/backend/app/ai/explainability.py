"""
Wraps the retrieval + generation + guardrail steps into a single explainable
answer object. Every recommendation the app shows a user must be able to
trace back to: what sources were retrieved, how confident the model is, and
why (in plain language). This is what powers the "92% confidence · Source:
WHO Hydration Guidelines" style UI in the app's AI advice card.
"""
from app.ai.generation.generator import generate_answer
from app.ai.guardrails.domain_classifier import is_in_domain
from app.ai.retrieval.retriever import retrieve
from app.schemas.ai import AIAnswer, SourceCitation

OFF_TOPIC_REFUSAL = (
    "I'm trained only on hydration and water-intake science, so I can't help with that. "
    "Ask me about daily water goals, dehydration symptoms, electrolytes, exercise hydration, "
    "or anything else water-related."
)


def answer_question(question: str, user_context: dict, domain_centroid=None) -> AIAnswer:
    in_domain, domain_confidence = is_in_domain(question, domain_centroid)
    if not in_domain:
        return AIAnswer(
            text=OFF_TOPIC_REFUSAL,
            confidence=1.0,
            reasoning="Question failed the hydration-domain guardrail (keyword + embedding-similarity screen).",
            sources=[],
            is_in_domain=False,
        )

    hits = retrieve(question)
    passages = [h.text for h in hits]
    result = generate_answer(question, passages, user_context)

    # Confidence blends retrieval strength (are the sources actually relevant?)
    # with the domain-classifier confidence. This is a heuristic, not a
    # calibrated probability — replace with a trained confidence head once
    # you have labeled data on answer correctness.
    retrieval_confidence = sum(h.score for h in hits) / len(hits) if hits else 0.0
    confidence = round(min(1.0, 0.5 * retrieval_confidence + 0.5 * domain_confidence), 2)

    reasoning = (
        f"Retrieved {len(hits)} passage(s) from the hydration knowledge base "
        f"(avg. relevance {retrieval_confidence:.2f}) and grounded the answer in the user's profile."
        if hits
        else "No closely matching sources were found; answer is based on general hydration guidance in the base model."
    )

    return AIAnswer(
        text=result.text,
        confidence=confidence,
        reasoning=reasoning,
        sources=[
            SourceCitation(title=h.document_title, document_id=h.document_id, relevance_score=round(h.score, 3))
            for h in hits
        ],
        model_version=result.model_version,
        is_in_domain=True,
    )
