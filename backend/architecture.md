# Architecture Overview

Components:

- API (FastAPI) — Receives resume uploads, exposes webhook endpoints for n8n
- Resume Processor — Extracts text from PDFs/DOCX, normalizes, and stores metadata
- HF MCP Client — Sends resume text to a Hugging Face MCP server to extract skills and experience
- LinkedIn Scraper — Polite, rate-limited scraper using `httpx` + `BeautifulSoup` with proxy rotation
- Application Builder — Uses `jinja2` templates to craft personalized application messages
- Email Sender — Sends via SMTP or transactional API, supports retries and idempotency
- Orchestrator (n8n) — Coordinates the pipeline: upload -> extract -> search -> draft -> send

Non-functional concerns:

- Rate limiting & backoff: `tenacity` + `ratelimit` wrappers
- Logging: structured logs via `loguru`
- Monitoring: optional Sentry / Prometheus exporter hooks
- Security: secrets via environment variables, validate inputs, and avoid storing PII when not needed

Data flow:

1. Resume uploaded via API or dropped into an ingestion bucket
2. Resume Processor extracts text and normalizes
3. HF MCP Client returns extracted skills and entities
4. LinkedIn Scraper finds matching open roles, respecting robots.txt
5. Application Builder drafts messages; Email Sender delivers
6. Orchestration and status callbacks report progress back to n8n
