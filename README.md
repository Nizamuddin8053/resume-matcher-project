# Resume Matcher

An AI-powered resume-to-job matching platform. Users upload their resume, and the system uses NLP embeddings to semantically match it against real job postings — ranked by relevance, with full application details (location, salary, experience level, and a direct apply link).

Built as a full-stack project combining a secure FastAPI backend, a PostgreSQL database, and a React frontend, with a real machine learning pipeline for matching rather than simple keyword search.

## Features

- **Secure authentication** — BCrypt password hashing, strong password validation (uppercase, number, special character), JWT-based sessions
- **Email OTP verification** — 6-digit one-time code sent via Gmail SMTP, required before login
- **Resume upload & parsing** — supports PDF and DOCX, extracts raw text automatically
- **ML-based job matching** — uses `sentence-transformers` to generate semantic embeddings and rank jobs by cosine similarity to the resume, not just keyword overlap
- **Real job data** — seeded from a real-world LinkedIn job postings dataset (500+ listings) with actual titles, descriptions, locations, salary ranges, work type, experience level, and application links
- **Resume management** — upload multiple resumes, delete old ones
- **Match results dashboard** — ranked job cards with match percentage, job details, and a direct "Apply Now" link to the original posting

## Tech Stack

**Backend**
- FastAPI (Python)
- PostgreSQL + SQLAlchemy (ORM) + Alembic (migrations)
- JWT authentication (`python-jose`) + BCrypt hashing (`passlib`)
- `sentence-transformers` (all-MiniLM-L6-v2) for semantic embeddings
- `pypdf` / `python-docx` for resume text extraction
- Gmail SMTP for OTP email delivery

**Frontend**
- React (Vite)
- React Router for navigation
- Axios for API requests
- `react-hot-toast` for notifications
- `lucide-react` for icons

## Project Structure

```
resume-matcher/
├── backend/
│   ├── main.py           # FastAPI app & routes
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── auth.py           # JWT + password hashing logic
│   ├── database.py       # DB connection & session
│   ├── email_utils.py    # OTP email sending
│   ├── resume_parser.py  # PDF/DOCX text extraction
│   ├── matcher.py        # Embedding + similarity scoring
│   ├── seed_jobs.py      # Bulk-loads job postings dataset
│   └── alembic/          # Database migrations
└── frontend/
    └── src/
        ├── components/    # Login, Register, VerifyOtp, Dashboard
        ├── api.js         # Centralized Axios client
        └── App.jsx        # Routes
```

## Setup

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:
```
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/resume_matcher
SECRET_KEY=<your-secret-key>
GMAIL_ADDRESS=<your-gmail-address>
GMAIL_APP_PASSWORD=<your-gmail-app-password>
```

Run migrations and start the server:
```bash
alembic upgrade head
uvicorn main:app --reload
```

Seed real job postings (optional — requires a `data/job_postings.csv` from the [LinkedIn Job Postings dataset](https://www.kaggle.com/datasets)):
```bash
python seed_jobs.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

## How Matching Works

1. Resume text and each job description are converted into vector embeddings using a pretrained sentence-transformer model.
2. Cosine similarity is computed between the resume vector and every job vector.
3. Results are ranked by similarity score (0–100%) and returned with full job details.

This captures semantic meaning rather than exact keyword matches — for example, "backend developer with API experience" and "engineer skilled in server-side development" score as similar despite sharing almost no identical words.

## Future Improvements

- Skill extraction and highlighting (show matched skills per job)
- Search and filter for the job listings independent of matching
- Match history page
- Deployment (Render/Railway + Vercel)
