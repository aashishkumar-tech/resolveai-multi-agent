from __future__ import annotations

from langchain_groq import ChatGroq

from app.core.config import settings


def get_llm() -> ChatGroq:
    return ChatGroq(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        api_key=settings.groq_api_key,
    )
