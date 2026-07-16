from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.explainability import answer_question
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.ai_recommendation import AIRecommendation, RecommendationKind
from app.models.user import User
from app.schemas.ai import AIAnswer, ChatRequest

router = APIRouter(prefix="/ai", tags=["ai"])


def _user_context(user: User) -> dict:
    return {
        "age": user.age,
        "gender": user.gender,
        "weight_kg": user.weight_kg,
        "activity_level": user.activity_level.value if user.activity_level else None,
        "city": user.city,
        "pregnant": user.pregnant,
        "breastfeeding": user.breastfeeding,
    }


@router.post("/chat", response_model=AIAnswer)
async def chat(
    payload: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ask the hydration coach a free-form question. The domain guardrail
    (app/ai/guardrails/domain_classifier.py) rejects anything outside
    hydration/water-intake science before the generator ever runs.
    """
    answer = answer_question(payload.question, _user_context(user))

    db.add(
        AIRecommendation(
            user_id=user.id,
            kind=RecommendationKind.CHAT_ANSWER,
            prompt=payload.question,
            output_text=answer.text,
            confidence=answer.confidence,
            reasoning=answer.reasoning,
            retrieved_sources=[s.model_dump() for s in answer.sources],
            model_version=answer.model_version,
        )
    )
    await db.commit()
    return answer


@router.get("/daily-advice", response_model=AIAnswer)
async def daily_advice(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Proactive, personalized hydration advice for right now — shown on the home dashboard."""
    prompt = (
        "Based on my current intake today, my profile, today's weather, and any recent exercise, "
        "how much more water should I drink, and when?"
    )
    answer = answer_question(prompt, _user_context(user))

    db.add(
        AIRecommendation(
            user_id=user.id,
            kind=RecommendationKind.DAILY_ADVICE,
            prompt=prompt,
            output_text=answer.text,
            confidence=answer.confidence,
            reasoning=answer.reasoning,
            retrieved_sources=[s.model_dump() for s in answer.sources],
            model_version=answer.model_version,
        )
    )
    await db.commit()
    return answer
