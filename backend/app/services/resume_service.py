import os
from typing import Dict, Any
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from app.core.logging import get_logger

logger = get_logger("resume_service")


def extract_text_from_file(path: str) -> str:
    """Extract text from common resume file formats using specialized libraries.
    
    Uses pdfminer.six for PDFs and python-docx for DOCX files to ensure 
    compatibility on Windows without external command-line dependencies.
    """
    try:
        suffix = os.path.splitext(path)[1].lower()
        
        if suffix == ".pdf":
            text = extract_pdf_text(path)
        elif suffix == ".docx":
            doc = Document(path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif suffix == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            # Fallback to a very simple byte read if extension unknown
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                
        logger.info("Extracted text from file", path=path, method=suffix)
        return text.strip()
    except Exception as e:
        logger.exception("Failed to extract text from resume")
        raise RuntimeError(f"Text extraction failed: {str(e)}")


def summarize_resume(text: str) -> Dict[str, Any]:
    """Placeholder for light-weight summarization/cleanup before sending to MCP.

    In production this could run lightweight NLP to remove PII or normalize content.
    """
    normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return {"raw_text": normalized}
