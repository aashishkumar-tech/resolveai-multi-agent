import logging
import os

logger = logging.getLogger(__name__)


def setup_langsmith():
    """Enable LangSmith tracing if API key is present."""
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "resolveai-multi-agent")
        logger.info("LangSmith tracing enabled")
    else:
        logger.warning("LANGCHAIN_API_KEY not set — tracing disabled")
