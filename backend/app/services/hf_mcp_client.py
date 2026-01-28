import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("hf_mcp_client")


class MCPClientError(Exception):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10),
       retry=retry_if_exception_type((httpx.RequestError, MCPClientError)))
def extract_entities_from_text(text: str, timeout: int = 30) -> Dict[str, Any]:
    """Send text to a Hugging Face MCP server endpoint and return parsed entities.

    Expects the MCP server to expose a JSON POST endpoint that accepts `text` and returns
    structured JSON with fields like `skills`, `experience`, `positions`.

    Retries on transient network errors.
    """
    if not settings.HF_MCP_URL:
        logger.error("HF_MCP_URL is not configured")
        raise MCPClientError("MCP server URL not configured")

    headers = {"Authorization": f"Bearer {settings.HF_MCP_TOKEN}"} if settings.HF_MCP_TOKEN else {}
    payload = {"text": text}

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(settings.HF_MCP_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logger.debug("MCP response received", response=data)
            return data
    except httpx.HTTPStatusError as e:
        logger.error("MCP server returned bad status", status=e.response.status_code, text=e.response.text)
        raise MCPClientError(f"MCP server error: {e.response.status_code}")
    except httpx.RequestError as e:
        logger.exception("Network error communicating with MCP server")
        raise
