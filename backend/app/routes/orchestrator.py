from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from app.core.logging import get_logger
from app.services.hf_mcp_client import extract_entities_from_text

router = APIRouter()
logger = get_logger("orchestrator")


class ResumeUpload(BaseModel):
    text: str
    email: str


@router.post("/webhook/ingest")
async def ingest_resume(payload: ResumeUpload, background_tasks: BackgroundTasks):
    # Simple webhook entry: accept resume text and enqueue background processing
    try:
        background_tasks.add_task(process_resume_job, payload.dict())
        return {"status": "accepted"}
    except Exception as e:
        logger.exception("Failed to accept job")
        raise HTTPException(status_code=500, detail=str(e))


async def process_resume_job(payload: dict):
    # 1. Send to MCP for extraction
    text = payload.get("text")
    email = payload.get("email")
    try:
        entities = extract_entities_from_text(text)
        logger.info("Entities extracted", entities=entities)
        # TODO: orchestrate scraper -> application drafting -> email send
    except Exception:
        logger.exception("Error processing resume in background")
