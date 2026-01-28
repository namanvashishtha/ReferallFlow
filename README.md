# 🚀 ReferralFlow: Automated Job Application Pipeline

ReferralFlow is an intelligent, automated recruitment pipeline that matches your resume to open job roles and automates the application process. By combining **AI-driven text extraction**, **polite web scraping**, and **automated orchestration**, it turns the tedious task of job hunting into a streamlined, hands-off experience.

---

## 🌟 Key Features

-   🧠 **AI Resume Parsing:** Extracts skills, experience, and titles using Hugging Face MCP models.
-   🕵️ **Polite LinkedIn Scraper:** Discovers matching roles using proxy rotation and rate-limiting to respect platform terms.
-   🛠️ **Orchestration Layer:** Managed by **n8n** for seamless flow between resume ingestion and final outreach.
-   � **Direct File Upload:** No AWS required! Upload resumes (PDF/Docx) directly via API.
-   �📧 **Personalized Outreach:** Automatically drafts and sends custom application emails using Jinja2 templates.
-   📊 **Campaign Management:** Track progress and application statuses in a structured database.

---

## 🏗️ System Architecture

The application is built on a modular microservices-inspired architecture:

1.  **FastAPI Backend:** The core engine handling business logic, DB interactions, and external service clients.
2.  **n8n Workflow:** The "brain" that coordinates when a resume is uploaded, when to trigger the extraction, and when to send emails.
3.  **HF MCP Client:** A specialized service that communicates with Hugging Face for deep resume analysis.
4.  **SMTP/Transactional Email:** Handles the final delivery of your job applications.

### The Flow
```mermaid
graph LR
    A[Resume Upload] --> B[n8n Workflow]
    B --> C[FastAPI Backend]
    C --> D[AI Entity Extraction]
    D --> E[LinkedIn Scraper]
    E --> F[Personalized Drafting]
    F --> G[Email Delivery]
    G --> H[Success Tracking]
```

---

## 🛠️ Technology Stack

-   **Backend:** Python 3.9+, FastAPI, SQLAlchemy, Pydantic.
-   **Scraping:** HTTPX, BeautifulSoup4.
-   **Orchestration:** n8n.
-   **Database:** PostgreSQL / SQLite.
-   **AI Infrastructure:** Hugging Face MCP (Model Context Protocol).
-   **Emailing:** aiosmtplib.

---

## 🚀 Getting Started

### 1. Prerequisites
-   Python 3.9+
-   PostgreSQL (optional, defaults to SQLite if configured)
-   n8n (local or cloud instance)

### 2. Backend Setup
Navigate to the `backend` directory and install dependencies:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configuration
Copy the `.env.example` to `.env` and fill in your credentials:
```powershell
cp .env.example .env
```
Key variables to configure:
-   `DATABASE_URL`: Your database connection string.
-   `HF_MCP_URL`: URL to your Hugging Face extraction service.
-   `SMTP_USER` & `SMTP_PASSWORD`: For automated emailing.

### 4. Running the Application
You can use the provided batch file in the root directory:
```powershell
.\run_backend.bat
```
Or manually via uvicorn:
```powershell
uvicorn app.main:app --reload
```

---

## 🔄 n8n Integration (Alternative Flows)

### Option A: No Cloud (Local Files)
If you don't have AWS, replace the **S3** node in n8n with the **Local File Trigger** node. This will watch a folder on your computer for new resumes.

### Option B: Direct API Upload
You can skip n8n for ingestion and call the backend directly:
```bash
curl -X POST "http://localhost:8000/api/v1/orchestrator/upload?email=user@example.com" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@resume.pdf;type=application/pdf"
```

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.

---
*Developed with ❤️ for efficient job hunting.*
