import React, { useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Home, BarChart3, Target, FileText, MapPin, Users, CheckCircle2, Award, TrendingUp } from "lucide-react";
import Shell from "../common/Shell.jsx";
import SectionTitle from "../common/SectionTitle.jsx";
import StatCard from "../common/StatCard.jsx";
import { T } from "../../theme.js";
import { stats, placementTrend, skillGaps, providers, districts } from "../../data/admin.js";

const NAV = [
  { id: "overview", label: "Overview", icon: Home },
  { id: "placement", label: "Placement analytics", icon: BarChart3 },
  { id: "skillgap", label: "Skill gap analysis", icon: Target },
  { id: "provider", label: "Provider performance", icon: FileText },
  { id: "district", label: "District analysis", icon: MapPin },
];

const STAT_ICONS = [Users, CheckCircle2, Award, TrendingUp];

export default function AdminDashboard() {
  const [tab, setTab] = useState("overview");

  return (
    <Shell nav={NAV} active={tab} onNav={setTab} title="Programme overview" subtitle="1 Jan 2025 \u2013 31 May 2025">
      {tab === "overview" && (
        <>
          <div style={{ display: "flex", gap: 16, marginBottom: 22, flexWrap: "wrap" }}>
            {stats.map((s, i) => (
              <StatCard key={s.label} {...s} icon={STAT_ICONS[i]} />
            ))}
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20 }}>
            <div className="sk-card" style={{ padding: 22 }}>
              <SectionTitle action="Monthly">Placement rate trend</SectionTitle>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={placementTrend}>
                  <CartesianGrid stroke={T.borderSoft} vertical={false} />
                  <XAxis dataKey="m" stroke={T.textFaint} fontSize={11} tickLine={false} axisLine={false} />
                  <YAxis stroke={T.textFaint} fontSize={11} tickLine={false} axisLine={false} unit="%" />
                  <Tooltip contentStyle={{ background: T.bgElev2, border: `1px solid ${T.border}`, fontSize: 12, borderRadius: 8 }} />
                  <Line type="monotone" dataKey="rate" stroke={T.teal} strokeWidth={2.5} dot={{ r: 3, fill: T.teal }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="sk-card" style={{ padding: 22 }}>
              <SectionTitle>Top in-demand skills</SectionTitle>
              {skillGaps.slice(0, 5).map((s) => (
                <div key={s.skill} style={{ marginBottom: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                    <span style={{ fontSize: 12.5 }}>{s.skill}</span>
                    <span className="sk-mono" style={{ fontSize: 11.5, color: T.textDim }}>
                      {s.demand}%
                    </span>
                  </div>
                  <div style={{ height: 6, background: T.bgElev2, borderRadius: 4 }}>
                    <div style={{ width: `${s.demand}%`, height: "100%", background: T.taupe, borderRadius: 4 }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {tab === "placement" && (
        <div className="sk-card" style={{ padding: 22 }}>
          <SectionTitle action="Jan \u2013 Jun 2025">Placement rate trend</SectionTitle>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={placementTrend}>
              <CartesianGrid stroke={T.borderSoft} vertical={false} />
              <XAxis dataKey="m" stroke={T.textFaint} fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke={T.textFaint} fontSize={12} tickLine={false} axisLine={false} unit="%" />
              <Tooltip contentStyle={{ background: T.bgElev2, border: `1px solid ${T.border}`, fontSize: 12, borderRadius: 8 }} />
              <Line type="monotone" dataKey="rate" stroke={T.teal} strokeWidth={2.5} dot={{ r: 4, fill: T.teal }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {tab === "skillgap" && (
        <div className="sk-card" style={{ padding: 22 }}>
          <SectionTitle action="Demand vs trainee proficiency">Skill gap analysis</SectionTitle>
          {skillGaps.map((s) => (
            <div key={s.skill} style={{ marginBottom: 18 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 13 }}>{s.skill}</span>
                <span className="sk-mono" style={{ fontSize: 11.5, color: T.textDim }}>
                  gap {s.demand - s.proficiency}pt
                </span>
              </div>
              <div style={{ height: 8, background: T.bgElev2, borderRadius: 4, position: "relative" }}>
                <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${s.proficiency}%`, background: T.teal, borderRadius: 4 }} />
                <div style={{ position: "absolute", left: `${s.demand}%`, top: -3, bottom: -3, width: 2, background: T.tan }} />
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "provider" && (
        <div className="sk-card" style={{ padding: 22 }}>
          <SectionTitle>Provider performance \u2014 placement rate</SectionTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={providers} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={T.borderSoft} horizontal={false} />
              <XAxis type="number" stroke={T.textFaint} fontSize={11} tickLine={false} axisLine={false} unit="%" />
              <YAxis type="category" dataKey="name" stroke={T.textFaint} fontSize={12} tickLine={false} axisLine={false} width={140} />
              <Tooltip contentStyle={{ background: T.bgElev2, border: `1px solid ${T.border}`, fontSize: 12, borderRadius: 8 }} />
              <Bar dataKey="rate" fill={T.teal} radius={[0, 6, 6, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {tab === "district" && (
        <div className="sk-card" style={{ padding: 22 }}>
          <SectionTitle>Placement rate by district</SectionTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={districts} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={T.borderSoft} horizontal={false} />
              <XAxis type="number" stroke={T.textFaint} fontSize={11} tickLine={false} axisLine={false} unit="%" />
              <YAxis type="category" dataKey="name" stroke={T.textFaint} fontSize={12} tickLine={false} axisLine={false} width={110} />
              <Tooltip contentStyle={{ background: T.bgElev2, border: `1px solid ${T.border}`, fontSize: 12, borderRadius: 8 }} />
              <Bar dataKey="rate" fill={T.taupe} radius={[0, 6, 6, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </Shell>
  );
}
