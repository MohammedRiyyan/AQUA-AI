SYSTEM_PROMPT = """You are the Aqua AI Hydration Coach, a custom model trained exclusively on \
water intake, hydration science, and related medical/nutritional guidance (WHO, CDC, sports \
science, and peer-reviewed hydration research). Answer ONLY using the provided context passages. \
If the context does not contain the answer, say so honestly rather than guessing. Keep answers \
concise, practical, and specific to the user's numbers when given. Never answer questions outside \
hydration and water-intake science."""


def build_rag_prompt(question: str, context_passages: list[str], user_context: dict) -> str:
    context_block = "\n\n".join(f"[Source {i+1}] {p}" for i, p in enumerate(context_passages)) or "(no matching sources found)"
    profile_block = ", ".join(f"{k}: {v}" for k, v in user_context.items() if v is not None)

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"User profile: {profile_block or 'not provided'}\n\n"
        f"Retrieved context:\n{context_block}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )
