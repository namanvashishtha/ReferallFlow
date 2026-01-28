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


from app.services.linkedin_scraper import PoliteLinkedInScraper
from app.services.application_service import render_application_template
from app.services.emailer import send_email
import re

async def process_resume_job(payload: dict):
    """The main orchestration logic for the recruitment pipeline."""
    text = payload.get("text")
    email = payload.get("email")
    
    logger.info("Starting background processing for resume", email=email)
    
    # 1. Extract Entities (AI or Basic Fallback)
    entities = {}
    try:
        entities = extract_entities_from_text(text)
        logger.info("AI Entities extracted", entities=entities)
    except Exception as e:
        logger.warning("AI Extraction failed or not configured, using fallback keyword matching", error=str(e))
        # Basic fallback: extract common tech keywords
        common_skills = ["python", "javascript", "react", "fastapi", "sql", "aws", "docker", "kubernetes"]
        found_skills = [s for s in common_skills if s in text.lower()]
        entities = {
            "top_skills": found_skills or ["Software Engineering"],
            "years_of_experience": "X",
            "candidate_name": "Applicant",
            "positions": ["Software Engineer"]
        }

    # 2. Search for Jobs
    scraper = PoliteLinkedInScraper()
    jobs = []
    try:
        # Search for the first position found
        search_query = entities.get("positions", ["Software Engineer"])[0]
        logger.info(f"Searching LinkedIn for: {search_query}")
        
        # Simulating search URLs (In production these would be generated based on location/role)
        query_urls = [f"https://www.linkedin.com/jobs/search?keywords={search_query.replace(' ', '%20')}"]
        jobs = await scraper.search_jobs(query_urls, max_results=3)
        logger.info(f"Found {len(jobs)} jobs")
    except Exception:
        logger.exception("Job search failed")
    finally:
        await scraper.close()

    # 3. Draft and "Send" Applications
    if not jobs:
        logger.warning("No jobs found to apply to.")
        return

    for job in jobs:
        try:
            context = {
                "recruiter_name": "Hiring Manager",
                "position_title": job.get("title") or "Engineering Role",
                "company_name": job.get("company") or "your company",
                "top_skills": entities.get("top_skills", []),
                "years_of_experience": entities.get("years_of_experience", "3+"),
                "accomplishments": ["Developed scalable backends", "Optimized cloud costs"],
                "company_interest_reason": "your innovative work in the industry",
                "candidate_name": entities.get("candidate_name", "Naman"),
                "candidate_email": email,
                "candidate_phone": "+1-234-567-890"
            }
            
            draft = render_application_template("application_email.txt", context)
            logger.info(f"Drafted application for {job.get('company')}")
            
            # 4. Email Outreach
            subject = f"Application for {context['position_title']} - {context['candidate_name']}"
            
            # Log the draft so user can see it without SMTP setup
            logger.info("DRAFT CREATED:\n" + "="*20 + "\n" + draft + "\n" + "="*20)
            
            try:
                await send_email(email, subject, draft)
                logger.info(f"Email sent successfully to {email}")
            except Exception:
                logger.warning("Email sending failed (Check SMTP settings in .env). Draft is logged above.")
        
        except Exception:
            logger.exception(f"Failed to process application for {job.get('company')}")

    logger.info("Resume processing job completed")


