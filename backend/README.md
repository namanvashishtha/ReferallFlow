# Recruitment Automation Pipeline (Backend)

This backend provides services for a scalable recruitment automation pipeline:

- Resume ingestion and parsing
- Skill/experience extraction via Hugging Face MCP server
- LinkedIn scraping (polite, rate-limited, proxy-capable)
- Personalized application drafting and email delivery
- Webhook endpoints to integrate with n8n for orchestration

See `architecture.md` for the high-level design and `app/core/config.py` for configuration.

Quick start (development):

1. Create a virtual environment and install deps:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill secrets.
3. Run the FastAPI app (example):

```powershell
uvicorn app.main:app --reload
```

Notes:
- This repo is scaffolded for production-grade concerns: retries, rate limiting, proxy rotation, structured logging, and observability hooks.
- Respect target sites' Terms of Service. Use proxies and delays to avoid abuse. The LinkedIn scraper is designed to be polite and configurable.
