import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.jwt import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models.employer import Employer
from app.models.employment import EmploymentRecord
from app.models.followup import FollowUp
from app.models.skill import Skill
from app.models.trainee import Trainee
from app.models.training import TrainingEnrollment, TrainingProgram
from app.models.user import User, UserRole


@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    admin = User(name="Admin", email="admin@test.local", password_hash=hash_password("password"), role=UserRole.ADMIN)
    trainee_one = User(name="Trainee One", email="one@test.local", password_hash=hash_password("password"), role=UserRole.TRAINEE)
    trainee_two = User(name="Trainee Two", email="two@test.local", password_hash=hash_password("password"), role=UserRole.TRAINEE)
    employer_one = User(name="Employer One", email="employer1@test.local", password_hash=hash_password("password"), role=UserRole.EMPLOYER)
    employer_two = User(name="Employer Two", email="employer2@test.local", password_hash=hash_password("password"), role=UserRole.EMPLOYER)
    provider_one = User(name="Provider One", email="provider1@test.local", password_hash=hash_password("password"), role=UserRole.PROVIDER)
    provider_two = User(name="Provider Two", email="provider2@test.local", password_hash=hash_password("password"), role=UserRole.PROVIDER)
    db.add_all([admin, trainee_one, trainee_two, employer_one, employer_two, provider_one, provider_two])
    db.flush()
    t1 = Trainee(user_id=trainee_one.id, education="Diploma", location="Pune")
    t2 = Trainee(user_id=trainee_two.id, education="Degree", location="Nagpur")
    e1 = Employer(company_name="One Ltd", user_id=employer_one.id)
    e2 = Employer(company_name="Two Ltd", user_id=employer_two.id)
    p1 = TrainingProgram(name="Python", provider="Provider One", provider_user_id=provider_one.id)
    p2 = TrainingProgram(name="SQL", provider="Provider Two", provider_user_id=provider_two.id)
    db.add_all([t1, t2, e1, e2, p1, p2])
    db.flush()
    record = EmploymentRecord(trainee_id=t1.trainee_id, employer_id=e2.employer_id, job_role="Analyst", salary=1000)
    enrollment = TrainingEnrollment(trainee_id=t1.trainee_id, program_id=p2.program_id)
    db.add_all([record, enrollment])
    db.commit()
    ids = {"t1": t1.trainee_id, "t2": t2.trainee_id, "e1": e1.employer_id, "e2": e2.employer_id, "p1": p1.program_id, "p2": p2.program_id, "enrollment": enrollment.enrollment_id}
    tokens = {key: create_access_token({"sub": str(user.id), "role": user.role.value}) for key, user in {
        "admin": admin, "trainee": trainee_one, "other_trainee": trainee_two,
        "employer": employer_one, "other_employer": employer_two,
        "provider": provider_one, "other_provider": provider_two,
    }.items()}
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as test_client:
        test_client.test_ids = ids
        test_client.test_tokens = tokens
        yield test_client
    app.dependency_overrides.clear()
    db.close()
    Base.metadata.drop_all(engine)


def headers(client, role):
    return {"Authorization": f"Bearer {client.test_tokens[role]}"}


def test_authentication_rejects_missing_and_invalid_tokens(client):
    assert client.get("/api/v1/analytics/dashboard").status_code == 401
    assert client.get("/api/v1/analytics/dashboard", headers={"Authorization": "Bearer invalid"}).status_code == 401


def test_trainee_cannot_access_another_trainees_records(client):
    other_id = client.test_ids["t2"]
    assert client.put(f"/api/v1/trainees/{other_id}", headers=headers(client, "trainee"), json={"location": "Changed"}).status_code == 403
    assert client.post(f"/api/v1/trainees/{other_id}/skills", headers=headers(client, "trainee"), json={"skills": [{"name": "Python", "level": "ADVANCED"}]}).status_code == 403
    assert client.get(f"/api/v1/training/enrollments/{other_id}", headers=headers(client, "trainee")).status_code == 403
    assert client.get(f"/api/v1/employment/{other_id}", headers=headers(client, "trainee")).status_code == 403
    assert client.get(f"/api/v1/followups/{other_id}", headers=headers(client, "trainee")).status_code == 403


def test_employer_and_provider_ownership_is_enforced(client):
    assert client.post("/api/v1/employment", headers=headers(client, "employer"), json={"trainee_id": client.test_ids["t1"], "employer_id": client.test_ids["e2"], "job_role": "Analyst", "salary": 1000}).status_code == 403
    assert client.put("/api/v1/employment/1", headers=headers(client, "employer"), json={"status": "RESIGNED"}).status_code == 403
    assert client.get("/api/v1/training/mine/enrollments", headers=headers(client, "provider")).status_code == 200
    assert client.put(f"/api/v1/training/enrollment/{client.test_ids['enrollment']}", headers=headers(client, "provider"), json={"status": "COMPLETED"}).status_code == 403
    other_programs = client.get("/api/v1/training/mine", headers=headers(client, "other_provider")).json()["data"]
    assert all(item["program_id"] != client.test_ids["p1"] for item in other_programs)


def test_admin_only_endpoints_reject_non_admin(client):
    assert client.get("/api/v1/analytics/dashboard", headers=headers(client, "trainee")).status_code == 403
    assert client.patch(f"/api/v1/employers/{client.test_ids['e1']}/verification", headers=headers(client, "trainee"), json={"verification_status": True}).status_code == 403
