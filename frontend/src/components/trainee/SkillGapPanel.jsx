import React, { useState } from "react";
import { Search, AlertTriangle, CheckCircle, XCircle, TrendingUp } from "lucide-react";
import SectionTitle from "../common/SectionTitle.jsx";
import ProgressRing from "../common/ProgressRing.jsx";
import SkillBar from "../common/SkillBar.jsx";
import { T } from "../../theme.js";
import { getTraineeSkillGap, ApiError } from "../../services/api.js";

/* ─────────────────────────────────────────────────────────────────────────
   Constants
───────────────────────────────────────────────────────────────────────── */

const LEVEL_PERCENT = { BEGINNER: 33, INTERMEDIATE: 66, ADVANCED: 100 };

/** Map a BEGINNER/INTERMEDIATE/ADVANCED string or numeric proficiency to 0-100. */
function toPercent(value) {
  if (typeof value === "number") return Math.round(value);
  return LEVEL_PERCENT[String(value).toUpperCase()] ?? 0;
}

/* ─────────────────────────────────────────────────────────────────────────
   Sub-components
───────────────────────────────────────────────────────────────────────── */

function ScoreRing({ value, label }) {
  const clamped = Math.max(0, Math.min(100, Math.round(value ?? 0)));
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
      <ProgressRing value={clamped} size={100} />
      <span style={{ fontSize: 12, color: T.textDim, textAlign: "center" }}>{label}</span>
    </div>
  );
}

function SkillChip({ name, variant }) {
  const styles = {
    matched: { bg: T.tealSoft, fg: T.teal, border: T.tealDeep },
    missing: { bg: "#2A1515", fg: T.danger, border: "#4A1F1F" },
  };
  const s = styles[variant] || styles.matched;
  return (
    <span
      style={{
        display: "inline-block",
        background: s.bg,
        color: s.fg,
        border: `1px solid ${s.border}`,
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 500,
        padding: "4px 10px",
        margin: "3px 4px 3px 0",
      }}
    >
      {name}
    </span>
  );
}

function RecommendationCard({ item, index }) {
  const priority = item.priority_score ?? 0;
  const priorityLabel = priority >= 60 ? "High" : priority >= 30 ? "Medium" : "Low";
  const priorityColor = priority >= 60 ? T.danger : priority >= 30 ? T.amber : T.textDim;
  return (
    <div
      style={{
        background: T.bgElev2,
        border: `1px solid ${T.border}`,
        borderRadius: 10,
        padding: "14px 16px",
        marginBottom: 10,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <span style={{ fontSize: 13, fontWeight: 600, color: T.text }}>
            {index + 1}. {item.skill}
          </span>
          <small
            style={{
              display: "block",
              fontSize: 11.5,
              color: T.textDim,
              marginTop: 3,
              textTransform: "capitalize",
            }}
          >
            {item.reason}
          </small>
        </div>
        <span
          style={{
            fontSize: 11,
            fontWeight: 700,
            color: priorityColor,
            background: `${priorityColor}20`,
            borderRadius: 999,
            padding: "3px 9px",
            whiteSpace: "nowrap",
          }}
        >
          {priorityLabel} priority
        </span>
      </div>
      {typeof item.priority_score === "number" && (
        <div style={{ marginTop: 10 }}>
          <div style={{ height: 4, background: T.bgElev, borderRadius: 4, overflow: "hidden" }}>
            <div
              style={{
                height: "100%",
                width: `${Math.min(100, item.priority_score)}%`,
                background: priorityColor,
                borderRadius: 4,
                transition: "width 0.4s ease",
              }}
            />
          </div>
          <span style={{ fontSize: 10, color: T.textFaint, marginTop: 3, display: "block" }}>
            Priority score: {item.priority_score.toFixed(1)}
          </span>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────
   Error resolvers
───────────────────────────────────────────────────────────────────────── */

function resolveErrorMessage(err) {
  if (!(err instanceof ApiError)) {
    return {
      heading: "Connection error",
      detail: err.message || "Unable to reach the server. Check your connection and try again.",
      canRetry: true,
    };
  }

  if (err.errorCode === "ML_FEATURES_INCOMPLETE") {
    const missing = Array.isArray(err.data?.missing_fields) ? err.data.missing_fields : [];
    return {
      heading: "Profile data incomplete",
      detail:
        missing.length > 0
          ? `The following required data is missing: ${missing.join(", ")}. Complete your profile and skills before running this analysis.`
          : "Required profile or skill data is missing. Please update your Skills and Profile tabs first.",
      canRetry: false,
    };
  }

  if (err.errorCode === "ML_SERVICE_UNAVAILABLE" || err.status === 503) {
    return {
      heading: "Analysis service unavailable",
      detail: "The ML analysis service is temporarily unavailable. Please try again in a few minutes.",
      canRetry: true,
    };
  }

  if (err.errorCode === "ML_MODEL_UNAVAILABLE") {
    return {
      heading: "Model not ready",
      detail: "The prediction model is currently unavailable. Please try again shortly.",
      canRetry: true,
    };
  }

  if (err.status === 403) {
    return {
      heading: "Access denied",
      detail: "You are not authorised to request this analysis.",
      canRetry: false,
    };
  }

  if (err.status === 404) {
    return {
      heading: "Profile not found",
      detail: "Your trainee profile could not be found. Please contact support.",
      canRetry: false,
    };
  }

  return {
    heading: "Analysis failed",
    detail: err.message || "An unexpected error occurred. Please try again.",
    canRetry: true,
  };
}

/* ─────────────────────────────────────────────────────────────────────────
   Main component
───────────────────────────────────────────────────────────────────────── */

/**
 * SkillGapPanel
 *
 * @param {number} traineeId - from profile.trainee_id loaded by TraineeDashboard (never from URL)
 * @param {Array}  skills    - current trainee skills array (for empty-state guard)
 */
export default function SkillGapPanel({ traineeId, skills = [] }) {
  const [jobRole, setJobRole] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const hasSkills = Array.isArray(skills) && skills.length > 0;

  const analyze = async (event) => {
    event.preventDefault();
    const role = jobRole.trim();
    if (!role) return;

    setAnalyzing(true);
    setResult(null);
    setError(null);

    try {
      // Frontend -> Backend /api/v1/trainees/{id}/ml/skill-gap -> ML service
      // Never calls the ML service or port 8001 directly.
      const envelope = await getTraineeSkillGap(traineeId, role);
      // envelope = { success, message, data, error_code }
      // envelope.data = SkillGapResponse from ML service
      setResult(envelope.data);
    } catch (err) {
      // 403 "Cannot access another trainee's ML analysis" -> treat as session error
      if (err instanceof ApiError && err.status === 403) {
        window.dispatchEvent(new Event("skilloutcome:unauthorized"));
        return;
      }
      setError(resolveErrorMessage(err));
    } finally {
      setAnalyzing(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  /* ── No skills guard ── */
  if (!hasSkills) {
    return (
      <div className="sk-card panel">
        <SectionTitle>Skill Gap Analysis</SectionTitle>
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 12,
            padding: "32px 0",
            textAlign: "center",
          }}
        >
          <AlertTriangle size={32} color={T.amber} />
          <p style={{ color: T.textDim, fontSize: 14, maxWidth: 380, lineHeight: 1.6 }}>
            You need to add at least one skill before running a skill gap analysis.
            <br />
            Visit the <strong style={{ color: T.text }}>Skills</strong> tab to add your skills first.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="sk-card panel">
      <SectionTitle>Skill Gap Analysis</SectionTitle>
      <p style={{ fontSize: 13, color: T.textDim, marginBottom: 20, lineHeight: 1.6 }}>
        Enter a target job role to see how your current skills compare against its requirements.
      </p>

      {/* ── Input form (hidden once results are shown) ── */}
      {!result && (
        <form onSubmit={analyze} style={{ display: "flex", gap: 10, marginBottom: 24, alignItems: "center" }}>
          <div style={{ position: "relative", flex: 1 }}>
            <Search
              size={15}
              color={T.textFaint}
              style={{ position: "absolute", left: 13, top: "50%", transform: "translateY(-50%)" }}
            />
            <input
              className="sk-input"
              style={{ paddingLeft: 38 }}
              placeholder="e.g. Data Analyst, Software Engineer..."
              value={jobRole}
              onChange={(e) => setJobRole(e.target.value)}
              disabled={analyzing}
              required
            />
          </div>
          <button className="sk-btn-primary" type="submit" disabled={analyzing || !jobRole.trim()}>
            {analyzing ? "Analysing..." : "Analyse Gap"}
          </button>
        </form>
      )}

      {/* ── Loading ── */}
      {analyzing && (
        <div style={{ textAlign: "center", padding: "28px 0" }}>
          <p style={{ color: T.textDim, fontSize: 13 }}>
            Analysing your skill profile against <strong style={{ color: T.text }}>{jobRole}</strong>...
          </p>
        </div>
      )}

      {/* ── Error ── */}
      {error && (
        <div
          style={{
            background: "#2A1515",
            border: "1px solid #4A1F1F",
            borderRadius: 12,
            padding: "16px 18px",
            marginBottom: 20,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <AlertTriangle size={16} color={T.danger} />
            <strong style={{ fontSize: 13, color: T.danger }}>{error.heading}</strong>
          </div>
          <p style={{ fontSize: 12.5, color: T.textDim, lineHeight: 1.6, margin: "0 0 12px" }}>
            {error.detail}
          </p>
          {error.canRetry && (
            <button className="text-button" onClick={reset} style={{ fontSize: 12.5 }}>
              Try again
            </button>
          )}
        </div>
      )}

      {/* ── Results ── */}
      {result && !analyzing && (
        <div className="sk-fade">
          {/* Header: role label + reset button */}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 22,
              paddingBottom: 14,
              borderBottom: `1px solid ${T.borderSoft}`,
            }}
          >
            <div>
              <span className="eyebrow">Results for</span>
              <h3 className="sk-display" style={{ fontSize: 18, marginTop: 2 }}>
                {result.target_job_role || jobRole}
              </h3>
            </div>
            <button
              className="sk-btn-ghost"
              onClick={reset}
              style={{ fontSize: 12, padding: "8px 14px" }}
            >
              New analysis
            </button>
          </div>

          {/* Score rings */}
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              gap: 40,
              marginBottom: 28,
              padding: "20px 0",
              background: T.bgElev2,
              borderRadius: 12,
              border: `1px solid ${T.borderSoft}`,
            }}
          >
            <ScoreRing
              value={result.skill_gap_score ?? 0}
              label="Skill Gap Score"
            />
            <ScoreRing
              value={result.skill_coverage_percent ?? 0}
              label="Skill Coverage %"
            />
          </div>

          {/* Matched skills */}
          <div style={{ marginBottom: 22 }}>
            <SectionTitle>
              <span style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <CheckCircle size={14} color={T.teal} />
                Matched Skills
                <span className="sk-mono" style={{ fontSize: 12, color: T.textFaint }}>
                  ({(result.matched_skills ?? []).length})
                </span>
              </span>
            </SectionTitle>
            {(result.matched_skills ?? []).length === 0 ? (
              <p style={{ color: T.textDim, fontSize: 13 }}>
                None of your current skills match this role's requirements.
              </p>
            ) : (
              <div style={{ paddingTop: 4 }}>
                {(result.matched_skills ?? []).map((name) => (
                  <SkillChip key={name} name={name} variant="matched" />
                ))}
              </div>
            )}
          </div>

          {/* Missing skills */}
          <div style={{ marginBottom: 22 }}>
            <SectionTitle>
              <span style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <XCircle size={14} color={T.danger} />
                Missing Skills
                <span className="sk-mono" style={{ fontSize: 12, color: T.textFaint }}>
                  ({(result.missing_skills ?? []).length})
                </span>
              </span>
            </SectionTitle>
            {(result.missing_skills ?? []).length === 0 ? (
              <p style={{ color: T.teal, fontSize: 13 }}>
                No missing skills — great match for this role!
              </p>
            ) : (
              <div style={{ paddingTop: 4 }}>
                {(result.missing_skills ?? []).map((name) => (
                  <SkillChip key={name} name={name} variant="missing" />
                ))}
              </div>
            )}
          </div>

          {/* Below-required proficiency
              Field names from src/modeling/features.py skill_gap_analysis():
                { skill, current_proficiency, required_proficiency, deficit }
          */}
          {(result.below_required_proficiency ?? []).length > 0 && (
            <div style={{ marginBottom: 22 }}>
              <SectionTitle>Skills Below Required Proficiency</SectionTitle>
              {(result.below_required_proficiency ?? []).map((item) => (
                <div
                  key={item.skill}
                  style={{
                    marginBottom: 18,
                    paddingBottom: 14,
                    borderBottom: `1px solid ${T.borderSoft}`,
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "baseline",
                      marginBottom: 6,
                    }}
                  >
                    <span style={{ fontSize: 13, color: T.text, fontWeight: 500 }}>
                      {item.skill}
                    </span>
                    <span className="sk-mono" style={{ fontSize: 11, color: T.amber }}>
                      deficit: {item.deficit != null ? item.deficit.toFixed(1) : "—"}
                    </span>
                  </div>
                  {/* SkillBar: level=current, target=required (target renders as a marker line) */}
                  <SkillBar
                    name=""
                    level={Math.round(item.current_proficiency ?? 0)}
                    target={Math.round(item.required_proficiency ?? 0)}
                  />
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontSize: 11,
                      color: T.textFaint,
                      marginTop: 3,
                    }}
                  >
                    <span>Current: {Math.round(item.current_proficiency ?? 0)}%</span>
                    <span>Required: {Math.round(item.required_proficiency ?? 0)}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recommendations
              Field names from src/modeling/features.py skill_gap_analysis():
                { skill, priority_score, reason }
          */}
          {(result.recommendations ?? []).length > 0 && (
            <div style={{ marginBottom: 8 }}>
              <SectionTitle>
                <span style={{ display: "flex", alignItems: "center", gap: 7 }}>
                  <TrendingUp size={14} color={T.amber} />
                  Recommendations
                </span>
              </SectionTitle>
              {(result.recommendations ?? []).map((item, i) => (
                <RecommendationCard key={`${item.skill}-${i}`} item={item} index={i} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
