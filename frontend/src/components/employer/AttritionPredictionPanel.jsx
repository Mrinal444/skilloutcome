import React, { useState } from "react";
import SectionTitle from "../common/SectionTitle.jsx";
import { T } from "../../theme.js";
import { ApiError, predictAttrition } from "../../services/api.js";

export default function AttritionPredictionPanel() {
  const [form, setForm] = useState({
    employment_duration_months: 6,
    salary_lpa: 4,
    job_history: 1,
    engagement_score: 7,
    target_job_role: "",
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
      const response = await predictAttrition({
        ...form,
        employment_duration_months: Number(form.employment_duration_months),
        salary_lpa: Number(form.salary_lpa),
        job_history: Number(form.job_history),
        engagement_score: Number(form.engagement_score),
      });
      setResult(response.data);
    } catch (requestError) {
      setError(requestError instanceof ApiError ? requestError.message : "Unable to run attrition prediction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="sk-card panel" style={{ marginTop: 16 }}>
      <SectionTitle>Attrition risk prediction</SectionTitle>
      <p style={{ color: T.textDim, fontSize: 13 }}>Estimate retention risk for an employment record.</p>
      <form onSubmit={submit}>
        <input className="sk-input" required placeholder="Target job role" value={form.target_job_role}
          onChange={(event) => setForm({ ...form, target_job_role: event.target.value })} />
        <div className="two-grid">
          <input className="sk-input" type="number" min="0" required placeholder="Months employed"
            value={form.employment_duration_months} onChange={(event) => setForm({ ...form, employment_duration_months: event.target.value })} />
          <input className="sk-input" type="number" min="0" required placeholder="Salary (LPA)"
            value={form.salary_lpa} onChange={(event) => setForm({ ...form, salary_lpa: event.target.value })} />
        </div>
        <button className="sk-btn-primary" type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Predict attrition risk"}
        </button>
      </form>
      {error && <p className="form-error">{error}</p>}
      {result && <div style={{ marginTop: 16 }}>
        <strong>{result.risk} risk</strong>
        <p style={{ color: T.textDim }}>Estimated probability: {(result.attrition_probability * 100).toFixed(1)}%</p>
        {result.input_warnings?.length > 0 && <p className="muted">{result.input_warnings.join(" ")}</p>}
      </div>}
    </div>
  );
}
