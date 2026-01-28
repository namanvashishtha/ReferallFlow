from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
import os
import shutil
import tempfile
from pydantic import BaseModel
from app.core.logging import get_logger
from app.services.hf_mcp_client import extract_entities_from_text
from app.services.resume_service import extract_text_from_file

router = APIRouter()
logger = get_logger("orchestrator")


class ResumeTextPayload(BaseModel):
    text: str
    email: str


@router.post("/webhook/ingest")
async def ingest_resume(payload: ResumeTextPayload, background_tasks: BackgroundTasks):
    # Simple webhook entry: accept resume text and enqueue background processing
    try:
        background_tasks.add_task(process_resume_job, payload.dict())
        return {"status": "accepted"}
    except Exception as e:
        logger.exception("Failed to accept job")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_resume(
    background_tasks: BackgroundTasks,
    email: str,
    file: UploadFile = File(...),
):
    """Directly upload a resume file (PDF, DOCX) and start the pipeline."""
    try:
        # Create a temporary file to store the upload
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        # Extract text from the temporary file
        text = extract_text_from_file(tmp_path)
        
        # Cleanup the temporary file
        os.unlink(tmp_path)

        # Enqueue the processing job
        background_tasks.add_task(process_resume_job, {"text": text, "email": email})
        
        return {
            "status": "accepted",
            "filename": file.filename,
            "message": "File uploaded and processing started"
        }
    except Exception as e:
        logger.exception("Failed to process uploaded file")
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")


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

