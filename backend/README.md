# ⚙️ ReferralFlow: Backend Services

This directory contains the core services and API for the ReferralFlow pipeline. 

## 📂 Project Structure
- `app/routes`: FastAPI endpoints for auth, campaigns, and orchestration.
- `app/services`: Core logic for scraping, AI extraction, and email delivery.
- `app/models`: Database models (SQLAlchemy).
- `app/core`: Configuration and logging.

## 🛠️ Local Development

1. **Environment Setup:**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Database Migrations:**
   The project uses SQLAlchemy. Ensure your `DATABASE_URL` is set in `.env` before running migrations.

3. **Running the API:**
   ```powershell
   uvicorn app.main:app --reload
   ```

## 🔌 API Endpoints
- `POST /api/v1/orchestrator/webhook/ingest`: Entry point for resumes from n8n.
- `GET /health`: System health check.
- `AUTH`: Standard OAuth2/Auth0 integration for secure access.

## 🤖 Integrated Services
- **LinkedIn Scraper:** Uses `httpx` and `BeautifulSoup`. Configurable concurrency and proxy rotation.
- **MCP Client:** Communicates with Hugging Face Model Context Protocol for entity extraction.
- **Emailer:** Asynchronous SMTP delivery using `aiosmtplib`.

## 📜 Structured Logging
We use `loguru` for structured JSON logging, making it easy to trace jobs through the pipeline via correlation IDs.

---
*For high-level architecture and overall setup, please refer to the root [README](../README.md).*

