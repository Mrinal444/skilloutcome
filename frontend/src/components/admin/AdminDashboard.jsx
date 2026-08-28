import React, { useEffect, useMemo, useState } from "react";
import { BarChart3, Building2, Download, FileText, Home, MapPin, PhoneCall, Target, Users } from "lucide-react";
import Shell from "../common/Shell.jsx";
import SectionTitle from "../common/SectionTitle.jsx";
import StatCard from "../common/StatCard.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import { T } from "../../theme.js";
import { useI18n } from "../../i18n.jsx";
import {
  createFollowup, getDashboardAnalytics, getDistrictAnalytics, getFollowupHistory,
  getProviderAnalytics, getSkillGapAnalytics, getAllTrainees, getTrainee, getEmployers,
  updateEmployerVerification,
} from "../../services/api.js";

const NAV = [
  { id: "overview", label: "Overview", icon: Home },
  { id: "trainees", label: "Trainees", icon: Users },
  { id: "followups", label: "Follow-ups", icon: PhoneCall },
  { id: "providers", label: "Providers", icon: Building2 },
  { id: "districts", label: "Districts", icon: MapPin },
  { id: "skills", label: "Skill gaps", icon: Target },
  { id: "verification", label: "Verification", icon: Building2 },
  { id: "reports", label: "Reports", icon: FileText },
];
const empty = (items) => !Array.isArray(items) || items.length === 0;
const format = (value) => String(value || "").replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());

function State({ loading, error, items, emptyText }) {
  if (loading) return <p style={{ color: T.textDim }}>Loading...</p>;
  if (error) return <p className="form-error">{error}</p>;
  if (empty(items)) return <p style={{ color: T.textDim }}>{emptyText}</p>;
  return null;
}

export default function AdminDashboard() {
  const { t } = useI18n();
  const [tab, setTab] = useState("overview");
  const [refresh, setRefresh] = useState(0);
  const [data, setData] = useState({ overview: null, providers: [], districts: [], skills: [], trainees: [], employers: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [followup, setFollowup] = useState({ trainee_id: "", follow_up_type: "DAY_30", status: "EMPLOYED", salary: "", feedback: "" });
  const [notice, setNotice] = useState("");

  const load = async () => {
    setLoading(true); setError("");
    try {
      const responses = await Promise.all([
        getDashboardAnalytics(), getProviderAnalytics(), getDistrictAnalytics(),
        getSkillGapAnalytics(), getAllTrainees(), getEmployers(),
      ]);
      setData({
        overview: responses[0].data,
        providers: responses[1].data || [],
        districts: responses[2].data || [],
        skills: responses[3].data?.details || [],
        trainees: responses[4].data || [],
        employers: responses[5].data || [],
      });
    } catch (requestError) { setError(requestError.message || "Unable to load admin data."); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, [refresh]);

  const filteredTrainees = useMemo(() => data.trainees.filter((trainee) => {
    const haystack = `${trainee.user_name || ""} ${trainee.user_email || ""} ${trainee.location || ""}`.toLowerCase();
    return haystack.includes(search.toLowerCase());
  }), [data.trainees, search]);

  const inspect = async (trainee) => {
    try {
      const [response, followupResponse] = await Promise.all([getTrainee(trainee.trainee_id), getFollowupHistory(trainee.trainee_id)]);
      setSelected({ ...response.data, followups: followupResponse.data || [] });
    }
    catch (requestError) { setError(requestError.message || "Unable to load trainee details."); }
  };
  const submitFollowup = async (event) => {
    event.preventDefault();
    try {
      await createFollowup({ ...followup, trainee_id: Number(followup.trainee_id), salary: followup.salary ? Number(followup.salary) : null });
      setFollowup({ trainee_id: "", follow_up_type: "DAY_30", status: "EMPLOYED", salary: "", feedback: "" });
      setNotice("Follow-up recorded."); setRefresh((value) => value + 1);
    } catch (requestError) { setError(requestError.message || "Unable to record follow-up."); }
  };
  const toggleVerification = async (employer) => {
    try {
      await updateEmployerVerification(employer.employer_id, !employer.verification_status);
      setNotice("Verification status updated."); setRefresh((value) => value + 1);
    } catch (requestError) { setError(requestError.message || "Unable to update verification."); }
  };
  const exportReport = () => {
    const rows = [["Name", "Email", "Location", "Education", "Experience"]];
    data.trainees.forEach((item) => rows.push([item.user_name, item.user_email, item.location, item.education, item.experience]));
    const csv = rows.map((row) => row.map((value) => `"${String(value ?? "").replaceAll('"', '""')}"`).join(",")).join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const link = document.createElement("a"); link.href = url; link.download = "skilloutcome-trainees.csv"; link.click(); URL.revokeObjectURL(url);
    setNotice("Report exported.");
  };

  return <Shell nav={NAV} active={tab} onNav={setTab} title={NAV.find((item) => item.id === tab)?.label || "Admin"} subtitle="Live programme data">
    <div className="admin-toolbar"><div><h1 className="sk-display admin-heading">{NAV.find((item) => item.id === tab)?.label}</h1></div><div className="toolbar-actions"><button className="sk-btn-ghost" onClick={() => setRefresh((value) => value + 1)}>Refresh</button><button className="sk-btn-primary" onClick={exportReport}><Download size={14} /> Export</button></div></div>
    {notice && <p className="toast">{notice}</p>}{error && <p className="form-error">{error}</p>}
    {loading && tab !== "reports" ? <p>Loading admin workspace...</p> : <>
      {tab === "overview" && <div><div className="four-grid">{[["Total trainees", data.overview?.total_trainees], ["Placement rate", `${data.overview?.placement_rate ?? 0}%`], ["Retention rate", `${data.overview?.retention_rate ?? 0}%`], ["Average salary growth", `${data.overview?.average_salary_growth ?? 0}%`]].map(([label, value]) => <StatCard key={label} label={label} value={value ?? "—"} icon={BarChart3} />)}</div><div className="sk-card panel"><SectionTitle>Live programme overview</SectionTitle><p style={{ color: T.textDim }}>Metrics are calculated by the backend from current trainee, employment, and follow-up records.</p></div></div>}
      {tab === "trainees" && <div className="sk-card panel"><SectionTitle action={<input className="sk-input" placeholder="Search trainees" value={search} onChange={(event) => setSearch(event.target.value)} />}>Trainee management</SectionTitle><State loading={false} error={error} items={filteredTrainees} emptyText="No trainees found." /><div className="table-wrap"><table><thead><tr><th>Name</th><th>Email</th><th>Location</th><th>Education</th><th>Action</th></tr></thead><tbody>{filteredTrainees.map((trainee) => <tr key={trainee.trainee_id}><td>{trainee.user_name || "Unnamed"}</td><td>{trainee.user_email || "—"}</td><td>{trainee.location || "—"}</td><td>{trainee.education || "—"}</td><td><button className="text-button" onClick={() => inspect(trainee)}>Inspect</button></td></tr>)}</tbody></table></div></div>}
      {tab === "followups" && <div className="two-grid"><div className="sk-card panel"><SectionTitle>Record follow-up</SectionTitle><form onSubmit={submitFollowup}><select className="sk-input" required value={followup.trainee_id} onChange={(e) => setFollowup({ ...followup, trainee_id: e.target.value })}><option value="">Select trainee</option>{data.trainees.map((item) => <option key={item.trainee_id} value={item.trainee_id}>{item.user_name || item.trainee_id}</option>)}</select><select className="sk-input" value={followup.follow_up_type} onChange={(e) => setFollowup({ ...followup, follow_up_type: e.target.value })}><option>DAY_30</option><option>DAY_90</option><option>DAY_180</option></select><select className="sk-input" value={followup.status} onChange={(e) => setFollowup({ ...followup, status: e.target.value })}><option>EMPLOYED</option><option>UNEMPLOYED</option><option>SELF_EMPLOYED</option><option>FURTHER_TRAINING</option></select><input className="sk-input" type="number" min="0" placeholder="Salary (optional)" value={followup.salary} onChange={(e) => setFollowup({ ...followup, salary: e.target.value })} /><textarea className="sk-input" placeholder="Remarks" value={followup.feedback} onChange={(e) => setFollowup({ ...followup, feedback: e.target.value })} /><button className="sk-btn-primary" type="submit">Record follow-up</button></form></div><div className="sk-card panel"><SectionTitle>Follow-up history</SectionTitle><p style={{ color: T.textDim }}>Select a trainee in the Trainees tab to inspect their follow-up history.</p></div></div>}
      {tab === "providers" && <List title="Provider analytics" items={data.providers} fields={["provider", "total_enrollments", "completion_rate", "placement_rate", "average_salary"]} />}
      {tab === "districts" && <List title="District analytics" items={data.districts} fields={["location", "total_trainees", "placement_rate", "average_salary"]} />}
      {tab === "skills" && <List title="Skill gaps" items={data.skills} fields={["skill_name", "demand_count"]} />}
      {tab === "verification" && <div className="sk-card panel"><SectionTitle>Employer verification</SectionTitle><State loading={false} error="" items={data.employers} emptyText="No employer profiles found." />{data.employers.map((employer) => <div className="metric-row" key={employer.employer_id}><span><b>{employer.company_name}</b><small>{employer.industry || "Industry not recorded"} · {employer.location || "Location not recorded"}</small></span><button className="text-button" onClick={() => toggleVerification(employer)}><StatusBadge status={employer.verification_status ? "Verified" : "Pending"} /></button></div>)}</div>}
      {tab === "reports" && <div className="sk-card panel"><SectionTitle>Reports</SectionTitle><p style={{ color: T.textDim }}>Export currently loaded trainee data as CSV.</p><button className="sk-btn-primary" onClick={exportReport}><Download size={14} /> Export trainee report</button></div>}
    </>}
    {selected && <div className="sk-card panel" style={{ marginTop: 20 }}><SectionTitle action={<button className="text-button" onClick={() => setSelected(null)}>Close</button>}>Trainee details</SectionTitle><p><b>{selected.user_name || "Unnamed"}</b> · {selected.user_email || "No email"}</p><p>{selected.education || "Education not recorded"} · {selected.location || "Location not recorded"} · {selected.experience || 0} years experience</p><p>Skills: {(selected.skills || []).map((skill) => `${skill.skill_name} (${format(skill.level)})`).join(", ") || "None"}</p><p>Follow-ups: {(selected.followups || []).map((item) => `${format(item.follow_up_type)}: ${format(item.status)}`).join(", ") || "None recorded"}</p></div>}
  </Shell>;
}

function List({ title, items, fields }) {
  return <div className="sk-card panel"><SectionTitle>{title}</SectionTitle><State loading={false} error="" items={items} emptyText="No data available." />{items.length > 0 && <div className="table-wrap"><table><thead><tr>{fields.map((field) => <th key={field}>{format(field)}</th>)}</tr></thead><tbody>{items.map((item, index) => <tr key={index}>{fields.map((field) => <td key={field}>{item[field] ?? "—"}{field.includes("rate") ? "%" : ""}</td>)}</tr>)}</tbody></table></div>}</div>;
}
