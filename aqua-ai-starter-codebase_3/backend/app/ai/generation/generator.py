"""
Text generation for the hydration coach — runs entirely locally via
transformers. NO OpenAI / Anthropic / Gemini / Llama-API / DeepSeek / Grok or
any other hosted LLM is called anywhere in this module or the rest of the
codebase.

Model resolution order:
  1. settings.GENERATION_MODEL_PATH — your fine-tuned checkpoint. Point this
     at a local directory (output of your training run — see
     app/ai/ingestion/pipeline.py and the training docs in /docs) or a
     private HF Hub repo you control.
  2. settings.GENERATION_MODEL_FALLBACK — a small open-weight instruct model
     used as a placeholder so the RAG pipeline is runnable end-to-end before
     your fine-tune exists. Swap it out once step 1 is ready; nothing else
     in the codebase needs to change.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from app.ai.generation.prompt_templates import build_rag_prompt
from app.core.config import get_settings

settings = get_settings()


@dataclass
class GenerationResult:
    text: str
    model_version: str


@lru_cache
def _load_model():
    model_path = settings.GENERATION_MODEL_PATH
    resolved = model_path if os.path.isdir(model_path) else settings.GENERATION_MODEL_FALLBACK

    tokenizer = AutoTokenizer.from_pretrained(resolved)
    model = AutoModelForCausalLM.from_pretrained(
        resolved,
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    return tokenizer, model, resolved


def generate_answer(question: str, context_passages: list[str], user_context: dict) -> GenerationResult:
    tokenizer, model, resolved_name = _load_model()
    prompt = build_rag_prompt(question, context_passages, user_context)

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    if torch.cuda.is_available():
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=settings.MAX_NEW_TOKENS,
            temperature=0.4,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )

    generated = tokenizer.decode(output_ids[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return GenerationResult(text=generated.strip(), model_version=resolved_name)
