import logging
import re
import time

from groq import RateLimitError


logger = logging.getLogger(__name__)


def invoke_with_rate_limit_retry(llm, messages, max_attempts=6):
    """Retry Groq requests when the provider returns a temporary 429 limit."""
    for attempt in range(max_attempts):
        try:
            return llm.invoke(messages)
        except RateLimitError as exc:
            if attempt == max_attempts - 1:
                raise

            delay = _retry_delay(exc, attempt)
            logger.warning(
                "Groq rate limit reached; retrying in %.1f seconds (%d/%d)",
                delay,
                attempt + 1,
                max_attempts - 1,
            )
            time.sleep(delay)


def _retry_delay(exc, attempt):
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", {}) or {}
    retry_after = headers.get("retry-after")

    if retry_after:
        try:
            return min(max(float(retry_after), 0.5) + 0.2, 60)
        except (TypeError, ValueError):
            pass

    match = re.search(r"try again in\s+([\d.]+)\s*s", str(exc), re.IGNORECASE)
    if match:
        return min(max(float(match.group(1)), 0.5) + 0.2, 60)

    return min(2**attempt, 30)
