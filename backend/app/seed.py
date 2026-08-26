"""
Database seeder for SkillOutcome.
Generates synthetic data using Pandas and NumPy.

Run with: python -m app.seed
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.trainee import Trainee, TraineeSkill, SkillLevel
from app.models.skill import Skill
from app.models.training import TrainingProgram, TrainingEnrollment, EnrollmentStatus
from app.models.employer import Employer
from app.models.employment import EmploymentRecord, EmploymentStatus
from app.models.followup import FollowUp, FollowUpType, FollowUpStatus
from app.auth.jwt import hash_password

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# ── Configuration ──────────────────────────────────────────────────

TRAINEE_COUNT = 50
EMPLOYER_COUNT = 5
PROVIDER_COUNT = 5

SKILLS_DATA = [
    ("Python", "Technology"),
    ("SQL", "Technology"),
    ("Data Analysis", "Analytics"),
    ("Machine Learning", "AI"),
    ("Cloud Computing", "Technology"),
    ("JavaScript", "Technology"),
    ("Communication", "Soft Skills"),
    ("Excel", "Analytics"),
    ("PowerBI", "Analytics"),
    ("Statistics", "Mathematics"),
    ("Project Management", "Management"),
    ("DevOps", "Technology"),
    ("Cybersecurity", "Technology"),
    ("Digital Marketing", "Marketing"),
    ("Financial Literacy", "Finance"),
]

TRAINING_PROGRAMS = [
    ("Data Analytics Bootcamp", "3 Months", "Technology"),
    ("Full Stack Web Development", "6 Months", "Technology"),
    ("Cloud Engineering Certification", "4 Months", "Technology"),
    ("AI & Machine Learning Foundation", "5 Months", "AI"),
    ("Digital Marketing Mastery", "2 Months", "Marketing"),
    ("Cybersecurity Essentials", "3 Months", "Technology"),
    ("Business Analytics with Excel", "2 Months", "Analytics"),
    ("DevOps & CI/CD Pipeline", "3 Months", "Technology"),
    ("Financial Modelling", "2 Months", "Finance"),
    ("Soft Skills & Communication", "1 Month", "Soft Skills"),
]

PROVIDER_NAMES = [
    "NSDC Academy",
    "Skill India Digital",
    "TCS iON",
    "Infosys Springboard",
    "NASSCOM FutureSkills",
]

EMPLOYER_DATA = [
    ("ABC Technologies", "IT", "Bangalore"),
    ("DataCraft Solutions", "Analytics", "Hyderabad"),
    ("CyberShield India", "Cybersecurity", "Delhi"),
    ("GreenFin Services", "Finance", "Mumbai"),
    ("DigiReach Media", "Marketing", "Pune"),
]

LOCATIONS = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Pune",
    "Chennai", "Kolkata", "Jaipur", "Ahmedabad", "Lucknow",
]

EDUCATION_LEVELS = [
    "10th Pass", "12th Pass", "Diploma", "B.Tech", "B.Sc",
    "B.Com", "BCA", "M.Tech", "MBA", "MCA",
]

FIRST_NAMES = [
    "Rahul", "Priya", "Amit", "Sneha", "Vikram", "Anjali", "Rohit",
    "Deepika", "Arjun", "Kavita", "Suresh", "Neha", "Manish", "Pooja",
    "Rajesh", "Swati", "Arun", "Rina", "Sanjay", "Megha",
    "Karan", "Simran", "Varun", "Nisha", "Tushar", "Ritika", "Gaurav",
    "Sonali", "Nikhil", "Aarti", "Prakash", "Divya", "Harsh", "Pallavi",
    "Mohit", "Komal", "Vivek", "Tanvi", "Ashish", "Shweta",
    "Sachin", "Preeti", "Ankit", "Ruchi", "Kunal", "Jyoti",
    "Dhruv", "Meera", "Akash", "Shilpa",
]

LAST_NAMES = [
    "Sharma", "Singh", "Patel", "Kumar", "Gupta", "Reddy", "Joshi",
    "Verma", "Iyer", "Nair", "Das", "Mishra", "Chauhan", "Rao",
    "Malhotra", "Agarwal", "Tiwari", "Bhat", "Saxena", "Mehta",
]

JOB_ROLES = [
    "Data Analyst", "Software Developer", "Cloud Engineer",
    "ML Engineer", "Marketing Executive", "Security Analyst",
    "Business Analyst", "DevOps Engineer", "Financial Analyst",
    "Project Coordinator",
]


def seed():
    """Main seed function. Idempotent — checks before inserting."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding database with synthetic data...")

        # ── 1. Admin User ─────────────────────────────────────────
        admin = User(
            name="Admin User",
            email="admin@skilloutcome.gov.in",
            password_hash=hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        db.add(admin)
        db.flush()
        print(f"  [OK] Admin user created (email: admin@skilloutcome.gov.in, password: admin123)")

        # ── 2. Provider Users ─────────────────────────────────────
        provider_users = []
        for i, name in enumerate(PROVIDER_NAMES):
            pu = User(
                name=name,
                email=f"provider{i+1}@skilloutcome.gov.in",
                password_hash=hash_password("provider123"),
                role=UserRole.PROVIDER,
            )
            db.add(pu)
            provider_users.append(pu)
        db.flush()
        print(f"  [OK] {len(provider_users)} provider users created")

        # ── 3. Employer Users ─────────────────────────────────────
        employer_users = []
        for i, (company, industry, location) in enumerate(EMPLOYER_DATA):
            eu = User(
                name=company,
                email=f"employer{i+1}@skilloutcome.gov.in",
                password_hash=hash_password("employer123"),
                role=UserRole.EMPLOYER,
            )
            db.add(eu)
            employer_users.append(eu)
        db.flush()
        print(f"  [OK] {len(employer_users)} employer users created")

        # ── 4. Skills ─────────────────────────────────────────────
        skills = []
        for skill_name, category in SKILLS_DATA:
            s = Skill(skill_name=skill_name, category=category)
            db.add(s)
            skills.append(s)
        db.flush()
        print(f"  [OK] {len(skills)} skills created")

        # ── 5. Training Programs ──────────────────────────────────
        programs = []
        for i, (name, duration, category) in enumerate(TRAINING_PROGRAMS):
            provider_name = PROVIDER_NAMES[i % len(PROVIDER_NAMES)]
            p = TrainingProgram(
                name=name,
                provider=provider_name,
                duration=duration,
                category=category,
            )
            db.add(p)
            programs.append(p)
        db.flush()
        print(f"  [OK] {len(programs)} training programs created")

        # ── 6. Employers ─────────────────────────────────────────
        employers = []
        for company, industry, location in EMPLOYER_DATA:
            e = Employer(
                company_name=company,
                industry=industry,
                location=location,
                verification_status=True,
            )
            db.add(e)
            employers.append(e)
        db.flush()
        print(f"  [OK] {len(employers)} employers created")

        # ── 7. Trainee Users + Profiles ───────────────────────────
        trainees = []
        for i in range(TRAINEE_COUNT):
            first = FIRST_NAMES[i % len(FIRST_NAMES)]
            last = LAST_NAMES[i % len(LAST_NAMES)]
            full_name = f"{first} {last}"
            email = f"{first.lower()}.{last.lower()}{i+1}@gmail.com"

            user = User(
                name=full_name,
                email=email,
                password_hash=hash_password("trainee123"),
                role=UserRole.TRAINEE,
            )
            db.add(user)
            db.flush()

            trainee = Trainee(
                user_id=user.id,
                education=random.choice(EDUCATION_LEVELS),
                location=random.choice(LOCATIONS),
                experience=int(np.random.randint(0, 6)),
            )
            db.add(trainee)
            trainees.append(trainee)

        db.flush()
        print(f"  [OK] {len(trainees)} trainee profiles created")

        # ── 8. Assign Skills to Trainees ──────────────────────────
        skill_count = 0
        for trainee in trainees:
            num_skills = random.randint(2, 5)
            chosen_skills = random.sample(skills, num_skills)
            for skill in chosen_skills:
                ts = TraineeSkill(
                    trainee_id=trainee.trainee_id,
                    skill_id=skill.skill_id,
                    level=random.choice(list(SkillLevel)),
                )
                db.add(ts)
                skill_count += 1
        db.flush()
        print(f"  [OK] {skill_count} trainee-skill assignments created")

        # ── 9. Enrollments ────────────────────────────────────────
        enrollments = []
        base_date = datetime(2025, 1, 1)
        for trainee in trainees:
            num_programs = random.randint(1, 3)
            chosen_programs = random.sample(programs, num_programs)
            for program in chosen_programs:
                start = base_date + timedelta(days=random.randint(0, 365))
                status = random.choices(
                    list(EnrollmentStatus),
                    weights=[15, 70, 15],
                )[0]
                completion_date = None
                score = None
                if status == EnrollmentStatus.COMPLETED:
                    completion_date = start + timedelta(days=random.randint(30, 180))
                    score = round(float(np.random.uniform(50, 100)), 1)

                e = TrainingEnrollment(
                    trainee_id=trainee.trainee_id,
                    program_id=program.program_id,
                    start_date=start,
                    completion_date=completion_date,
                    status=status,
                    score=score,
                )
                db.add(e)
                enrollments.append(e)
        db.flush()
        print(f"  [OK] {len(enrollments)} enrollments created")

        # ── 10. Employment Records ────────────────────────────────
        emp_records = []
        completed_trainees = [
            t for t in trainees
            if any(
                e.status == EnrollmentStatus.COMPLETED
                for e in db.query(TrainingEnrollment)
                .filter(TrainingEnrollment.trainee_id == t.trainee_id)
                .all()
            )
        ]

        # ~80% of completed trainees get employed
        employed_trainees = random.sample(
            completed_trainees,
            int(len(completed_trainees) * 0.8),
        ) if completed_trainees else []

        for trainee in employed_trainees:
            employer = random.choice(employers)
            salary = round(float(np.random.uniform(300000, 1200000)), 0)
            joining = base_date + timedelta(days=random.randint(90, 500))

            # 85% still employed, 10% resigned, 5% terminated
            status = random.choices(
                list(EmploymentStatus),
                weights=[85, 10, 5],
            )[0]

            record = EmploymentRecord(
                trainee_id=trainee.trainee_id,
                employer_id=employer.employer_id,
                job_role=random.choice(JOB_ROLES),
                salary=salary,
                joining_date=joining,
                status=status,
            )
            db.add(record)
            emp_records.append(record)
        db.flush()
        print(f"  [OK] {len(emp_records)} employment records created")

        # ── 11. Follow-ups ────────────────────────────────────────
        followup_count = 0
        for record in emp_records:
            base_salary = record.salary
            for fu_type in [FollowUpType.DAY_30, FollowUpType.DAY_90, FollowUpType.DAY_180]:
                # Some trainees may not have all follow-ups
                if random.random() < 0.85:
                    if record.status == EmploymentStatus.EMPLOYED:
                        fu_status = random.choices(
                            [FollowUpStatus.EMPLOYED, FollowUpStatus.SELF_EMPLOYED],
                            weights=[90, 10],
                        )[0]
                    else:
                        fu_status = random.choices(
                            [FollowUpStatus.UNEMPLOYED, FollowUpStatus.FURTHER_TRAINING],
                            weights=[60, 40],
                        )[0]

                    # Salary grows slightly at each follow-up
                    multiplier = {"DAY_30": 1.0, "DAY_90": 1.05, "DAY_180": 1.12}
                    salary = round(base_salary * multiplier.get(fu_type.value, 1.0), 0)

                    feedback_options = [
                        "Working successfully",
                        "Good progress",
                        "Looking for better opportunities",
                        "Satisfied with role",
                        "Skill gap in advanced topics",
                        "Needs mentorship",
                        "Performing well",
                    ]

                    fu = FollowUp(
                        trainee_id=record.trainee_id,
                        follow_up_type=fu_type,
                        status=fu_status,
                        salary=salary if fu_status == FollowUpStatus.EMPLOYED else None,
                        feedback=random.choice(feedback_options),
                    )
                    db.add(fu)
                    followup_count += 1

        db.flush()
        print(f"  [OK] {followup_count} follow-up records created")

        db.commit()
        print("\n[SUCCESS] Database seeded successfully!")
        print(f"\nSummary:")
        print(f"   Users:        {db.query(User).count()}")
        print(f"   Trainees:     {db.query(Trainee).count()}")
        print(f"   Skills:       {db.query(Skill).count()}")
        print(f"   Programs:     {db.query(TrainingProgram).count()}")
        print(f"   Enrollments:  {db.query(TrainingEnrollment).count()}")
        print(f"   Employers:    {db.query(Employer).count()}")
        print(f"   Employment:   {db.query(EmploymentRecord).count()}")
        print(f"   Follow-ups:   {db.query(FollowUp).count()}")

        print(f"\nTest Credentials:")
        print(f"   Admin:    admin@skilloutcome.gov.in / admin123")
        print(f"   Provider: provider1@skilloutcome.gov.in / provider123")
        print(f"   Employer: employer1@skilloutcome.gov.in / employer123")
        print(f"   Trainee:  rahul.sharma1@gmail.com / trainee123")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
