# Database Design

## Database

PostgreSQL


## Main Entities


## Users

Stores authentication information.

Fields:

- id
- name
- email
- password_hash
- role


---

## Trainees

Stores trainee information.

Fields:

- trainee_id
- user_id
- education
- location
- experience


---

## Training Programs

Stores available courses.

Fields:

- program_id
- name
- provider
- duration
- category


---

## Skills

Stores skill information.

Fields:

- skill_id
- skill_name
- category


---

## Employment Records

Stores employment outcomes.

Fields:

- employment_id
- trainee_id
- company
- job_role
- salary
- joining_date
- status


---

## Relationships


User

↓

Trainee

↓

Training

↓

Employment

↓

Analytics