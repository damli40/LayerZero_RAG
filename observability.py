# observability.py
# PostHog LLM observability for the LayerZero RAG assistant.
#
# Uses PostHog's LangChain CallbackHandler (version-tolerant — works with the
# repo's langchain 0.1.x / langchain-openai 0.0.8 without monkeypatching). Call
# init_observability() once at process startup (done for you in the FastAPI app,
# the Telegram bot, the CLI, and start_enhanced.py). Then rag/query.py attaches a
# per-request handler to the gpt-4o generation, so each query is captured as a
# PostHog $ai_generation event (model, latency, input/output tokens, cost),
# grouped into one trace and attributed to the user.
#
# Everything is import-safe and a no-op when POSTHOG_API_KEY is unset or the
# posthog package is unavailable, so the app runs unchanged without it.

import os
import logging

logger = logging.getLogger("observability")

_initialized = False
_client = None  # posthog.Posthog client when enabled, else None


def init_observability():
    """Set up the PostHog client. Safe to call multiple times. Returns the client or None."""
    global _initialized, _client
    if _initialized:
        return _client
    _initialized = True

    api_key = os.getenv("POSTHOG_API_KEY")
    if not api_key:
        logger.info("PostHog observability disabled (POSTHOG_API_KEY not set).")
        return None

    try:
        from posthog import Posthog
    except Exception as exc:  # missing dep — don't crash the app
        logger.warning("PostHog observability unavailable (%s); skipping.", exc)
        return None

    host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")
    _client = Posthog(api_key, host=host)
    logger.info("PostHog observability enabled (host=%s).", host)
    return _client


def get_callback_handler(distinct_id="anonymous", trace_id=None, **properties):
    """Return a PostHog LangChain CallbackHandler for one request, or None if disabled.

    Pass the result in config={"callbacks": [handler]} on llm.invoke(...). Extra
    keyword args become event properties on the captured $ai_generation.
    """
    if _client is None:
        return None
    try:
        from posthog.ai.langchain import CallbackHandler
    except Exception as exc:
        logger.warning("PostHog CallbackHandler unavailable (%s).", exc)
        return None

    clean_props = {k: v for k, v in properties.items() if v is not None}
    return CallbackHandler(
        client=_client,
        distinct_id=str(distinct_id),
        trace_id=str(trace_id) if trace_id is not None else None,
        properties=clean_props or None,
    )
