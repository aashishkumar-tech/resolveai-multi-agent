from __future__ import annotations

import os

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

from app.core.config import settings


@tool
def search_web(query: str) -> str:
    """Search the web for recent information using Tavily."""

    # Ensure underlying Tavily wrapper can see the key.
    # Some wrappers read from os.environ instead of our Settings loader.
    os.environ.setdefault("TAVILY_API_KEY", settings.tavily_api_key)

    search = TavilySearchResults(
        top_k_results=1,
        doc_content_chars_max=500,
        tavily_api_key=settings.tavily_api_key,
    )
    results = search.invoke(query)
    return str(results)


@tool
def write_summary(content: str) -> str:
    """Summarize content (kept for parity; agent code will call LLM directly)."""
    from app.workflow.llm import get_llm

    llm = get_llm()
    prompt = (
        "Please provide a clear and concise summary of the following research findings:\n\n"
        f"{content}\n\nSummary:"
    )
    return llm.invoke(prompt).content
