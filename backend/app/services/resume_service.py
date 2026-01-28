import textract
from typing import Dict, Any
from app.core.logging import get_logger

logger = get_logger("resume_service")


def extract_text_from_file(path: str) -> str:
    """Extract text from common resume file formats using textract.

    This is a best-effort extractor; in production consider more robust parsing and virus scanning.
    """
    try:
        text = textract.process(path).decode("utf-8", errors="ignore")
        logger.info("Extracted text from file", path=path)
        return text
    except Exception:
        logger.exception("Failed to extract text from resume")
        raise


def summarize_resume(text: str) -> Dict[str, Any]:
    """Placeholder for light-weight summarization/cleanup before sending to MCP.

    In production this could run lightweight NLP to remove PII or normalize content.
    """
    normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return {"raw_text": normalized}
