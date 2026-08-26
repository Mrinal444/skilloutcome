# Backend — SkillOutcome

## Owner
Backend Team

## Purpose
Contains the backend services for SkillOutcome (SIH26135).

## Tech Stack

- FastAPI
- Python 3.13+
- SQLite (dev) / PostgreSQL (prod)
- SQLAlchemy ORM
- Pydantic validation
- JWT Authentication (python-jose)
- bcrypt password hashing

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy environment file
copy .env.example .env    # Windows
# cp .env.example .env     # Linux/Mac

# 4. Run the server
uvicorn app.main:app --reload

# 5. Seed the database with synthetic data
python -m app.seed
```

## API Docs

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Test Credentials (after seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@skilloutcome.gov.in | admin123 |
| Provider | provider1@skilloutcome.gov.in | provider123 |
| Employer | employer1@skilloutcome.gov.in | employer123 |
| Trainee | rahul.sharma1@gmail.com | trainee123 |

## API Endpoints

All endpoints are under `/api/v1`:

| Module | Endpoints |
|--------|-----------|
| Auth | POST /auth/register, POST /auth/login |
| Trainees | CRUD /trainees, POST /trainees/{id}/skills |
| Skills | GET /skills |
| Training | CRUD /training, POST /training/enroll |
| Employers | POST /employers, GET /employers/{id} |
| Employment | CRUD /employment |
| Follow-ups | POST /followups, GET /followups/{id} |
| Analytics | GET /analytics/dashboard, providers, skill-gaps, districts |

## Current Status

Project setup complete. All modules implemented.