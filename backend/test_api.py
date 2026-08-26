"""
Comprehensive integration test suite for SkillOutcome API endpoints.
Tests all routers, auth, RBAC, and data validation using FastAPI TestClient.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "SkillOutcome"
    print("[PASS] Health check")


def test_auth_login():
    # Admin login
    res = client.post("/api/v1/auth/login", json={
        "email": "admin@skilloutcome.gov.in",
        "password": "admin123"
    })
    assert res.status_code == 200
    body = res.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert body["data"]["role"] == "ADMIN"

    # Trainee login
    res_t = client.post("/api/v1/auth/login", json={
        "email": "rahul.sharma1@gmail.com",
        "password": "trainee123"
    })
    assert res_t.status_code == 200
    assert res_t.json()["data"]["role"] == "TRAINEE"

    # Invalid login
    res_bad = client.post("/api/v1/auth/login", json={
        "email": "admin@skilloutcome.gov.in",
        "password": "wrongpassword"
    })
    assert res_bad.status_code == 401
    print("[PASS] Auth login (Admin, Trainee, Invalid)")


def get_token(email, password):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return res.json()["data"]["access_token"]


def test_trainees_endpoints():
    admin_token = get_token("admin@skilloutcome.gov.in", "admin123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Get all trainees (admin only)
    res = client.get("/api/v1/trainees", headers=headers)
    assert res.status_code == 200
    trainees = res.json()["data"]
    assert len(trainees) > 0
    assert "trainee_id" in trainees[0]
    assert "skills" in trainees[0]

    # Get single trainee
    res_single = client.get(f"/api/v1/trainees/{trainees[0]['trainee_id']}", headers=headers)
    assert res_single.status_code == 200
    assert res_single.json()["data"]["trainee_id"] == trainees[0]["trainee_id"]

    print(f"[PASS] Trainees endpoints ({len(trainees)} trainees retrieved)")


def test_skills_endpoints():
    res = client.get("/api/v1/skills")
    assert res.status_code == 200
    skills = res.json()["data"]
    assert len(skills) >= 15
    print(f"[PASS] Skills endpoints ({len(skills)} skills available)")


def test_training_endpoints():
    res = client.get("/api/v1/training")
    assert res.status_code == 200
    programs = res.json()["data"]
    assert len(programs) >= 10

    # Get single program
    res_p = client.get(f"/api/v1/training/{programs[0]['program_id']}")
    assert res_p.status_code == 200
    print(f"[PASS] Training endpoints ({len(programs)} programs available)")


def test_employers_endpoints():
    admin_token = get_token("admin@skilloutcome.gov.in", "admin123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    res = client.get("/api/v1/employers/1", headers=headers)
    assert res.status_code == 200
    employer = res.json()["data"]
    assert employer["employer_id"] == 1
    assert "company_name" in employer
    print(f"[PASS] Employers endpoints (Employer: {employer['company_name']})")


def test_analytics_endpoints():
    admin_token = get_token("admin@skilloutcome.gov.in", "admin123")
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Dashboard analytics
    res_dash = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert res_dash.status_code == 200
    dash = res_dash.json()["data"]
    assert dash["total_trainees"] == 50
    assert "placement_rate" in dash
    assert "retention_rate" in dash
    assert "average_salary_growth" in dash

    # Provider analytics
    res_prov = client.get("/api/v1/analytics/providers", headers=headers)
    assert res_prov.status_code == 200
    provs = res_prov.json()["data"]
    assert len(provs) > 0

    # Skill gaps analytics
    res_gaps = client.get("/api/v1/analytics/skill-gaps", headers=headers)
    assert res_gaps.status_code == 200
    gaps = res_gaps.json()["data"]
    assert len(gaps["top_skill_gaps"]) > 0

    # District analytics
    res_dist = client.get("/api/v1/analytics/districts", headers=headers)
    assert res_dist.status_code == 200
    districts = res_dist.json()["data"]
    assert len(districts) > 0

    print(f"[PASS] Analytics endpoints:")
    print(f"       Dashboard -> Total: {dash['total_trainees']}, Placement: {dash['placement_rate']}%, Retention: {dash['retention_rate']}%, Avg Salary Growth: {dash['average_salary_growth']}%")
    print(f"       Providers -> {len(provs)} providers analyzed")
    print(f"       Skill Gaps -> Top gaps: {', '.join(gaps['top_skill_gaps'][:5])}")
    print(f"       Districts -> {len(districts)} districts analyzed")


def test_rbac():
    trainee_token = get_token("rahul.sharma1@gmail.com", "trainee123")
    headers = {"Authorization": f"Bearer {trainee_token}"}

    # Trainee trying to access admin analytics dashboard should be 403 Forbidden
    res = client.get("/api/v1/analytics/dashboard", headers=headers)
    assert res.status_code == 403
    print("[PASS] RBAC protection (Trainee blocked from Admin dashboard -> 403)")


if __name__ == "__main__":
    print("--- Running SkillOutcome API Integration Tests ---\n")
    test_health()
    test_auth_login()
    test_trainees_endpoints()
    test_skills_endpoints()
    test_training_endpoints()
    test_employers_endpoints()
    test_analytics_endpoints()
    test_rbac()
    print("\n--- ALL TESTS PASSED! ---")
