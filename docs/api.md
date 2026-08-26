
```markdown
# API Documentation

## Project

SkillOutcome

## Problem Statement

SIH26135 - Difficulties in tracking employment outcomes, skill gaps, and impact of skilling initiatives.

---

# API Base URL

All APIs follow versioning:

```
/api/v1
```

Example:

```
GET /api/v1/trainees
```

---

# Authentication

## Authorization Header

Protected APIs require:
Authorization: Bearer <JWT_TOKEN>

## Authentication Method

- JWT Token Based Authentication
- Role Based Access Control (RBAC)

## User Roles

| Role | Access |
|---|---|
| ADMIN | Government analytics and monitoring |
| TRAINEE | Personal profile and outcome tracking |
| PROVIDER | Training program management |
| EMPLOYER | Employment verification |

---

# Common API Response Format

## Success Response

```json
{
    "success": true,
    "message": "Operation successful",
    "data": {}
}
```

## Error Response

```json
{
    "success": false,
    "message": "Error description",
    "error_code": "ERROR_CODE"
}
```

---

# 1. Authentication APIs

---

# Register User

## Endpoint

```
POST /api/v1/auth/register
```

## Purpose

Creates a new user account.

## Access

Public

## Request

```json
{
    "name": "Rahul Sharma",
    "email": "rahul@gmail.com",
    "password": "password",
    "role": "TRAINEE"
}
```

## Response

```json
{
    "success": true,
    "message": "User registered successfully"
}
```

---

# Login User

## Endpoint

```
POST /api/v1/auth/login
```

## Purpose

Authenticates user and generates JWT token.

## Access

Public

## Request

```json
{
    "email": "rahul@gmail.com",
    "password": "password"
}
```

## Response

```json
{
    "success": true,
    "data": {
        "access_token": "jwt_token",
        "role": "TRAINEE"
    }
}
```

---

# 2. Trainee APIs

---

# Create Trainee Profile

## Endpoint

```
POST /api/v1/trainees
```

## Purpose

Creates trainee profile after registration.

## Access

TRAINEE / ADMIN


## Request

```json
{
    "education": "B.Tech",
    "location": "Mumbai",
    "experience": 1
}
```

---

# Get All Trainees

## Endpoint

```
GET /api/v1/trainees
```

## Purpose

Returns list of trainees.

## Access

ADMIN

---

# Get Trainee Profile

## Endpoint

```
GET /api/v1/trainees/{trainee_id}
```

## Purpose

Returns complete trainee information.

Includes:

- Personal details
- Skills
- Training history
- Employment status
- Predictions

---

# Update Trainee Profile

## Endpoint

```
PUT /api/v1/trainees/{trainee_id}
```

## Purpose

Updates trainee information.

---

# 3. Skills APIs

---

# Get Skills

## Endpoint

```
GET /api/v1/skills
```

## Purpose

Returns available skills.

---

# Add Skills To Trainee

## Endpoint

```
POST /api/v1/trainees/{trainee_id}/skills
```

## Purpose

Assigns skills to trainee.

## Request

```json
{
    "skills":[
        {
            "name":"Python",
            "level":"Advanced"
        },
        {
            "name":"SQL",
            "level":"Intermediate"
        }
    ]
}
```

---

# 4. Training Program APIs

---

# Create Training Program

## Endpoint

```
POST /api/v1/training
```

## Purpose

Training providers can add courses.

## Access

PROVIDER


## Request

```json
{
    "name":"Data Analytics",
    "duration":"3 Months",
    "category":"Technology"
}
```

---

# Get Training Programs

## Endpoint

```
GET /api/v1/training
```

## Purpose

Returns available training programs.

---

# Get Training Details

## Endpoint

```
GET /api/v1/training/{program_id}
```

---

# Enroll Trainee

## Endpoint

```
POST /api/v1/training/enroll
```

## Purpose

Enrolls trainee into a training program.

## Request

```json
{
    "trainee_id":101,
    "program_id":20
}
```

---

# Update Training Status

## Endpoint

```
PUT /api/v1/training/enrollment/{id}
```

## Purpose

Updates completion status.

Example:

```
ONGOING
COMPLETED
DROPPED
```

---

# 5. Employer APIs

---

# Register Employer

## Endpoint

```
POST /api/v1/employers
```

## Purpose

Creates employer profile.

## Request

```json
{
    "company_name":"ABC Technologies",
    "industry":"IT",
    "location":"Bangalore"
}
```

---

# Get Employer Details

## Endpoint

```
GET /api/v1/employers/{employer_id}
```

---

# 6. Employment Outcome APIs

---

# Add Employment Record

## Endpoint

```
POST /api/v1/employment
```

## Purpose

Stores employment outcome after training.

## Request

```json
{
    "trainee_id":101,
    "employer_id":20,
    "job_role":"Data Analyst",
    "salary":600000,
    "status":"EMPLOYED"
}
```

---

# Get Employment History

## Endpoint

```
GET /api/v1/employment/{trainee_id}
```

## Purpose

Returns complete employment journey.

---

# Update Employment Status

## Endpoint

```
PUT /api/v1/employment/{employment_id}
```

---

# 7. Follow-up APIs

---

# Add Follow-up Record

## Endpoint

```
POST /api/v1/followups
```

## Purpose

Tracks long-term outcomes.

Follow-up timeline:

- 30 days
- 90 days
- 180 days


## Request

```json
{
    "trainee_id":101,
    "status":"EMPLOYED",
    "salary":700000,
    "feedback":"Working successfully"
}
```

---

# Get Follow-up History

## Endpoint

```
GET /api/v1/followups/{trainee_id}
```

---

# 8. Analytics APIs

---

# Government Dashboard

## Endpoint

```
GET /api/v1/analytics/dashboard
```

## Purpose

Provides overall program insights.

Returns:

```json
{
    "total_trainees":10000,
    "placement_rate":82,
    "retention_rate":75,
    "average_salary_growth":15
}
```

---

# Provider Performance Analytics

## Endpoint

```
GET /api/v1/analytics/providers
```

## Purpose

Compare training providers.

Metrics:

- Placement rate
- Completion rate
- Retention
- Salary outcomes

---

# Skill Gap Analytics

## Endpoint

```
GET /api/v1/analytics/skill-gaps
```

## Purpose

Identify commonly missing skills.

Response:

```json
{
    "top_skill_gaps":[
        "Python",
        "Data Analysis",
        "Cloud Computing"
    ]
}
```

---

# District Analytics

## Endpoint

```
GET /api/v1/analytics/districts
```

## Purpose

Analyze outcomes geographically.

---

# 9. ML Intelligence APIs

---

# Placement Prediction

## Endpoint

```
POST /api/v1/ml/predict-placement
```

## Purpose

Predict probability of employment.

## Input

```json
{
    "education":"B.Tech",
    "skills":[
        "Python",
        "SQL"
    ],
    "attendance":90,
    "assessment_score":85
}
```

## Output

```json
{
    "placement_probability":0.82
}
```

---

# Attrition Prediction

## Endpoint

```
POST /api/v1/ml/predict-attrition
```

## Purpose

Predict employment dropout risk.

## Output

```json
{
    "risk":"MEDIUM"
}
```

---

# Skill Gap Prediction

## Endpoint

```
POST /api/v1/ml/skill-gap
```

## Purpose

Identify missing skills.

## Output

```json
{
    "missing_skills":[
        "PowerBI",
        "Statistics"
    ]
}
```

---

# Skill Recommendation

## Endpoint

```
POST /api/v1/ml/recommend-skills
```

## Purpose

Recommend skills required for career growth.

---

# 10. Admin APIs

---

# User Management

## Endpoint

```
GET /api/v1/admin/users
```

## Purpose

View system users.

Access:

ADMIN

---

# Audit Logs

## Endpoint

```
GET /api/v1/admin/logs
```

## Purpose

Monitor important system activities.

---

# Security Rules

## Public APIs

- Register
- Login
- Skill listing


## Protected APIs

Require JWT:

- Trainee data
- Employment data
- Analytics
- ML services
- Admin services


## Security Features

- Password hashing
- JWT authentication
- Role-based authorization
- Input validation
- API rate limiting


# Module Ownership

| Module | Owner |
|---|---|
| Authentication | Backend |
| Trainee APIs | Backend |
| Training APIs | Backend |
| Employment APIs | Backend |
| Analytics APIs | Backend + Frontend |
| ML APIs | AI Team |
| Dashboard APIs | Backend |
