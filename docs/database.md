# Database Design

## Database Technology

Technology: PostgreSQL

Reasons:
- Stores structured relational data
- Supports complex queries and analytics
- Provides strong consistency and reliability
- Suitable for government-scale applications


# Main Entities

The SkillOutcome platform uses the following main entities:

- Users
- Trainees
- Skills
- Training Programs
- Training Enrollment
- Employers
- Employment Records
- Follow-ups
- Skill Gap Analysis
- ML Predictions


# Entity Details


## Users

### Purpose
Stores authentication and authorization information.

### Fields

- id (Primary Key)
- name
- email
- password_hash
- role

### Relationship

User 1 ---- 1 Trainee



## Trainees

### Purpose
Stores trainee personal and professional information.

### Fields

- trainee_id (Primary Key)
- user_id (Foreign Key)
- education
- location
- experience


## Skills

### Purpose
Stores available skills and competency information.

### Fields

- skill_id (Primary Key)
- skill_name
- category



## Training Programs

### Purpose
Stores available training courses.

### Fields

- program_id (Primary Key)
- name
- provider
- duration
- category



## Training Enrollment

### Purpose
Tracks trainee participation in training programs.

### Fields

- enrollment_id
- trainee_id
- program_id
- start_date
- completion_date
- status
- score



## Employers

### Purpose
Stores employer information.

### Fields

- employer_id
- company_name
- industry
- location
- verification_status



## Employment Records

### Purpose
Stores employment outcomes after training.

### Fields

- employment_id
- trainee_id
- employer_id
- job_role
- salary
- joining_date
- status



## Skill Gap Analysis

### Purpose
Stores missing skills identified by comparing trainee skills with industry requirements.

### Fields

- analysis_id
- trainee_id
- required_skill
- current_level
- required_level
- gap_score



## ML Predictions

### Purpose
Stores machine learning prediction results.

### Fields

- prediction_id
- trainee_id
- prediction_type
- score
- model_version
- created_at



# Entity Relationships

USER
 |
 |
TRAINEE
 |
 |---------------- TRAINING ENROLLMENT ---------------- TRAINING PROGRAM
 |
 |---------------- EMPLOYMENT RECORD ------------------ EMPLOYER
 |
 |---------------- SKILL GAP ANALYSIS
 |
 |---------------- ML PREDICTIONS



 

# Relationship Explanation


## User - Trainee

One user account is linked to one trainee profile.


## Trainee - Skills

Many-to-many relationship.

A trainee can have multiple skills and a skill can belong to multiple trainees.


## Trainee - Training

One trainee can enroll in multiple training programs.


## Trainee - Employment

One trainee can have multiple employment records over time.


# Data Flow

Training Provider
        |
        ↓
Training Data
        |
        ↓
Trainee Profile
        |
        ↓
Employment Data
        |
        ↓
Analytics Engine
        |
        ↓
ML Predictions
        |
        ↓
Government Dashboard

