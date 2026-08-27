import React from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { User, Target, ClipboardList, Briefcase, Award, Building2, CheckCircle2 } from "lucide-react";
import Shell from "../common/Shell.jsx";
import { useLocation, useNavigate } from "react-router-dom";
import { useI18n } from "../../i18n.jsx";
import SectionTitle from "../common/SectionTitle.jsx";
import SkillBar from "../common/SkillBar.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import ProgressRing from "../common/ProgressRing.jsx";
import { T } from "../../theme.js";
import { traineeProfile, employment, skills, trainingHistory, salaryTrend, milestones } from "../../data/trainee.js";

const NAV = [
  { id: "profile", label: "Profile", icon: User },
  { id: "skills", label: "Skills", icon: Target },
  { id: "training", label: "Training history", icon: ClipboardList },
  { id: "employment", label: "Employment", icon: Briefcase },
  { id: "progress", label: "Progress", icon: Award },
];

export default function TraineeDashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const tab = location.pathname.split("/").filter(Boolean)[1] || "profile";
  const setTab = (next) => navigate(`/trainee/${next}`);

  return (
    <Shell
      nav={NAV}
      active={tab}
      onNav={setTab}
      title={traineeProfile.name}
      subtitle={`Trainee \u00b7 ${traineeProfile.trn} \u00b7 ${traineeProfile.location}`}
    >
      {tab === "profile" && (
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 20 }}>
          <div className="sk-card" style={{ padding: 22 }}>
            <SectionTitle>Current employment</SectionTitle>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", rowGap: 14, fontSize: 13 }}>
              {Object.entries(employment).map(([k, v]) => (
                <div key={k}>
                  <p style={{ color: T.textFaint, fontSize: 11.5, marginBottom: 3 }}>{k}</p>
                  <p style={{ color: T.text, fontSize: 13.5 }}>{v}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="sk-card" style={{ padding: 22 }}>
            <SectionTitle>Journey</SectionTitle>
            <div style={{ position: "relative", paddingLeft: 18 }}>
              <div style={{ position: "absolute", left: 4, top: 4, bottom: 4, width: 2, background: T.border }} />
              {milestones.slice().reverse().map((m, i) => (
                <div key={i} style={{ position: "relative", paddingBottom: 18 }}>
                  <div
                    style={{
                      position: "absolute",
                      left: -18,
                      top: 2,
                      width: 10,
                      height: 10,
                      borderRadius: "50%",
                      background: m.done ? T.teal : T.bgElev2,
                      border: `2px solid ${m.done ? T.teal : T.border}`,
                    }}
                  />
                  <p style={{ fontSize: 13, color: m.done ? T.text : T.textDim }}>{m.label}</p>
                  <p style={{ fontSize: 11.5, color: T.textFaint }}>{m.date}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {tab === "skills" && (
        <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20 }}>
          <div className="sk-card" style={{ padding: 22 }}>
            <SectionTitle action="Teal = current \u00b7 tan mark = programme target">Skill levels</SectionTitle>
            {skills.map((s) => (
              <SkillBar key={s.name} {...s} />
            ))}
          </div>
          <div className="sk-card" style={{ padding: 22, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <ProgressRing value={74} size={110} />
            <p style={{ fontSize: 13, color: T.textDim, marginTop: 14, textAlign: "center" }}>
              Average skill readiness against programme targets
            </p>
          </div>
        </div>
      )}

      {tab === "training" && (
        <div className="sk-card" style={{ padding: 22 }}>
          <SectionTitle>Training history</SectionTitle>
          {trainingHistory.map((t, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                padding: "14px 0",
                borderBottom: i < trainingHistory.length - 1 ? `1px solid ${T.borderSoft}` : "none",
              }}
            >
              <div>
                <p style={{ fontSize: 13.5, color: T.text }}>{t.name}</p>
                <p style={{ fontSize: 11.5, color: T.textFaint, marginTop: 3 }}>{t.date}</p>
              </div>
              <StatusBadge status={t.status} />
            </div>
          ))}
        </div>
      )}

      {tab === "employment" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
          <div className="sk-card" style={{ padding: 22 }}>
            <SectionTitle>Employment status</SectionTitle>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
              <div style={{ width: 44, height: 44, borderRadius: 10, background: T.tealSoft, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Building2 size={20} color={T.teal} />
              </div>
              <div>
                <p style={{ fontSize: 14, fontWeight: 500 }}>{employment.Company}</p>
                <p style={{ fontSize: 12, color: T.textDim }}>{employment.Role} \u00b7 {employment.Type}</p>
              </div>
              <div style={{ marginLeft: "auto" }}>
                <StatusBadge status="Placed" />
              </div>
            </div>
            <p style={{ fontSize: 12, color: T.textFaint }}>
              Retained 12 months on the job, 6-month retention milestone cleared.
            </p>
          </div>
          <div className="sk-card" style={{ padding: 22 }}>
            <SectionTitle>Salary progression</SectionTitle>
            <ResponsiveContainer width="100%" height={140}>
              <LineChart data={salaryTrend}>
                <CartesianGrid stroke={T.borderSoft} vertical={false} />
                <XAxis dataKey="m" stroke={T.textFaint} fontSize={11} tickLine={false} axisLine={false} />
                <YAxis hide />
                <Tooltip contentStyle={{ background: T.bgElev2, border: `1px solid ${T.border}`, fontSize: 12, borderRadius: 8 }} />
                <Line type="monotone" dataKey="v" stroke={T.teal} strokeWidth={2} dot={{ r: 3, fill: T.teal }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {tab === "progress" && (
        <div className="sk-card" style={{ padding: 26, display: "flex", gap: 32, alignItems: "center" }}>
          <ProgressRing value={78} size={130} />
          <div style={{ flex: 1 }}>
            <SectionTitle>Overall journey progress</SectionTitle>
            {milestones.map((m, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                <CheckCircle2 size={16} color={m.done ? T.teal : T.textFaint} />
                <span style={{ fontSize: 13, color: m.done ? T.text : T.textDim }}>{m.label}</span>
                <span style={{ fontSize: 11.5, color: T.textFaint, marginLeft: "auto" }}>{m.date}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Shell>
  );
}
