from src.modeling.features import normalize_skill, skill_gap_analysis, skills_to_text, training_performance


def test_skill_gap_prioritizes_missing_high_weight_skill():
    result = skill_gap_analysis(
        [{"name": "Python", "proficiency": 70}, {"name": "Excel", "proficiency": 90}],
        [{"name": "python", "required_proficiency": 80, "importance_weight": 0.4}, {"name": "sql", "required_proficiency": 75, "importance_weight": 0.6}],
    )
    assert result["missing_skills"] == ["sql"]
    assert result["matched_skills"] == ["python"]
    assert result["recommendations"][0]["skill"] == "sql"
    assert result["skill_gap_score"] > 0


def test_skill_gap_is_zero_when_every_requirement_is_met():
    result = skill_gap_analysis(
        [{"name": "Power BI", "proficiency": 90}, {"name": "SQL", "proficiency": 85}],
        [{"name": "power bi", "required_proficiency": 70, "importance_weight": 0.5}, {"name": "sql", "required_proficiency": 80, "importance_weight": 0.5}],
    )
    assert result["missing_skills"] == []
    assert result["skill_gap_score"] == 0.0
    assert result["skill_coverage_percent"] == 100.0
    assert result["recommendations"] == []


def test_skills_text_is_order_and_case_independent():
    assert skills_to_text(["SQL", "Power BI", "Python"]) == skills_to_text(["python", "sql", "power bi"])
    # Multi-word skills must survive as a single TF-IDF token.
    assert "power_bi" in skills_to_text(["Power BI"]).split()
    assert skills_to_text(["Python", "python ", "PYTHON"]) == "python"
    assert skills_to_text([" ", "", "SQL"]) == "sql"


def test_normalize_skill_keeps_technology_punctuation():
    assert normalize_skill("C++") == "c++"
    assert normalize_skill("Node.js") == "node.js"
    assert normalize_skill("  Power   BI ") == "power bi"


def test_training_performance_is_a_fixed_blend():
    assert training_performance(80, 90) == 84.5
    assert training_performance(100, 100) == 100.0
