# System Architecture

## Project Name

SkillOutcome

## Problem Statement

SIH26135 - Difficulties in tracking employment outcomes, skill gaps, and impact of skilling initiatives.

---

# High Level Architecture

The SkillOutcome platform follows a three-layer architecture:

1. Frontend Layer
2. Backend Layer
3. Intelligence/Data Layer


                 Users
                   |
                   |
            React Frontend
                   |
                   |
              REST APIs
                   |
                   |
            FastAPI Backend
                   |
        -----------------------
        |                     |
        |                     |
 PostgreSQL Database      ML Services
        |                     |
        |                     |
   Structured Data     Predictions


---

# Frontend Layer

Technology:

- React
- TypeScript
- Tailwind CSS

Responsibilities:

- User authentication interface
- Trainee dashboard
- Admin analytics dashboard
- Data visualization
- API communication


---

# Backend Layer

Technology:

- FastAPI
- Python
- SQLAlchemy
- PostgreSQL

Responsibilities:

- Authentication
- Business logic
- Data management
- API services
- Integration with ML services


---

# Database Layer

Technology:

PostgreSQL

Stores:

- User information
- Trainee profiles
- Training records
- Employment information
- Skill information
- Analytics data


---

# ML Intelligence Layer

Technology:

- Python
- Scikit-learn
- Pandas

Responsibilities:

- Placement prediction
- Attrition prediction
- Skill gap analysis
- Demand forecasting


---

# User Roles

## Trainee

Can:

- View profile
- Track training progress
- Update employment status
- View recommended skills


## Training Provider

Can:

- Manage courses
- Upload training data
- Monitor outcomes


## Employer

Can:

- Verify employment
- Provide job information


## Government Admin

Can:

- View analytics
- Monitor programs
- Identify skill gaps
- Make policy decisions