import logging
import re
import time

from groq import APIConnectionError, InternalServerError, RateLimitError


logger = logging.getLogger(__name__)

RETRYABLE_ERRORS = (RateLimitError, APIConnectionError, InternalServerError)
DURATION_UNITS = {"ms": 0.001, "s": 1, "m": 60, "h": 3600}
DURATION_PART = re.compile(r"([\d.]+)\s*(ms|h|m|s)")


def invoke_with_rate_limit_retry(llm, messages, max_attempts=4, max_total_wait=60):
    """Retry temporary Groq errors, with a bounded total wait per request."""
    waited = 0.0
    for attempt in range(max_attempts):
        try:
            return llm.invoke(messages)
        except RETRYABLE_ERRORS as exc:
            delay = _retry_delay(exc, attempt)
            if attempt == max_attempts - 1 or waited + delay > max_total_wait:
                raise

            logger.warning(
                "Groq request failed (%s); retrying in %.1f seconds (%d/%d)",
                type(exc).__name__,
                delay,
                attempt + 1,
                max_attempts - 1,
            )
            time.sleep(delay)
            waited += delay


def _retry_delay(exc, attempt):
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None) or {}
    retry_after = headers.get("retry-after")

    if retry_after:
        try:
            return max(float(retry_after), 0.5) + 0.2
        except (TypeError, ValueError):
            pass

    # Handles Groq messages such as "try again in 54.09s" and "7m12.5s".
    match = re.search(r"try again in\s+([\d.hms\s]+)", str(exc), re.IGNORECASE)
    if match:
        seconds = _parse_duration(match.group(1))
        if seconds is not None:
            return max(seconds, 0.5) + 0.2

    return min(2**attempt, 30)


def _parse_duration(text):
    parts = DURATION_PART.findall(text)
    if not parts:
        return None
    return sum(float(value) * DURATION_UNITS[unit] for value, unit in parts)
