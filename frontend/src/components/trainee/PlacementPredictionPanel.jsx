import React, { useState } from "react";
import SectionTitle from "../common/SectionTitle.jsx";
import { T } from "../../theme.js";
import { ApiError, predictPlacement } from "../../services/api.js";

export default function PlacementPredictionPanel({ profile, skills = [] }) {
  const [form, setForm] = useState({
    target_job_role: "",
    attendance_percent: 80,
    assessment_score: 70,
    training_duration_weeks: 12,
    previous_experience_years: profile?.experience || 0,
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const response = await predictPlacement({
        education_level: profile?.education || "Not specified",
        target_job_role: form.target_job_role.trim(),
        skills: skills.map((skill) => ({
          name: skill.skill_name,
          proficiency: { BEGINNER: 33, INTERMEDIATE: 66, ADVANCED: 100 }[skill.level] || 0,
        })),
        attendance_percent: Number(form.attendance_percent),
        assessment_score: Number(form.assessment_score),
        training_duration_weeks: Number(form.training_duration_weeks),
        previous_experience_years: Number(form.previous_experience_years),
      });
      setResult(response.data);
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "Unable to run placement prediction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sk-card panel" style={{ marginBottom: 16 }}>
      <SectionTitle>Placement prediction</SectionTitle>
      <p style={{ color: T.textDim, fontSize: 13 }}>
        Use your current profile and skills to estimate placement probability.
      </p>
      <form onSubmit={submit}>
        <input className="sk-input" required placeholder="Target job role" value={form.target_job_role}
          onChange={(event) => setForm({ ...form, target_job_role: event.target.value })} />
        <div className="two-grid">
          <input className="sk-input" type="number" min="0" max="100" required placeholder="Attendance %"
            value={form.attendance_percent} onChange={(event) => setForm({ ...form, attendance_percent: event.target.value })} />
          <input className="sk-input" type="number" min="0" max="100" required placeholder="Assessment score"
            value={form.assessment_score} onChange={(event) => setForm({ ...form, assessment_score: event.target.value })} />
        </div>
        <button className="sk-btn-primary" type="submit" disabled={loading || !skills.length}>
          {loading ? "Predicting..." : "Predict placement"}
        </button>
      </form>
      {!skills.length && <p className="muted">Add at least one skill before predicting placement.</p>}
      {error && <p className="form-error">{error}</p>}
      {result && <div style={{ marginTop: 16 }}>
        <strong>{result.placement_probability_percent}% placement probability</strong>
        <p style={{ color: T.textDim }}>Support priority: {result.support_priority}</p>
        {result.input_warnings?.length > 0 && <p className="muted">{result.input_warnings.join(" ")}</p>}
      </div>}
    </div>
  );
}
