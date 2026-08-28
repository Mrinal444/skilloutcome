import React, { useEffect, useState } from "react";
import { BookOpen, Users } from "lucide-react";
import Shell from "../common/Shell.jsx";
import SectionTitle from "../common/SectionTitle.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import { createTrainingProgram, getMyProviderEnrollments, getMyTrainingPrograms, updateEnrollment } from "../../services/api.js";

const NAV = [
  { id: "programmes", label: "My programmes", icon: BookOpen },
  { id: "enrollments", label: "Enrolments", icon: Users },
];

export default function ProviderDashboard() {
  const [tab, setTab] = useState("programmes");
  const [programs, setPrograms] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [form, setForm] = useState({ name: "", duration: "", category: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    setLoading(true); setError("");
    try {
      const [programResponse, enrollmentResponse] = await Promise.all([getMyTrainingPrograms(), getMyProviderEnrollments()]);
      setPrograms(programResponse.data || []);
      setEnrollments(enrollmentResponse.data || []);
    } catch (requestError) { setError(requestError.message || "Unable to load provider workspace."); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const createProgram = async (event) => {
    event.preventDefault();
    try {
      await createTrainingProgram(form);
      setForm({ name: "", duration: "", category: "" });
      setNotice("Programme created.");
      await load();
    } catch (requestError) { setError(requestError.message || "Unable to create programme."); }
  };

  const changeStatus = async (enrollment) => {
    const status = window.prompt("Status: ONGOING, COMPLETED, or DROPPED", enrollment.status);
    if (!status || !["ONGOING", "COMPLETED", "DROPPED"].includes(status.toUpperCase())) return;
    try {
      await updateEnrollment(enrollment.enrollment_id, { status: status.toUpperCase() });
      setNotice("Enrolment updated.");
      await load();
    } catch (requestError) { setError(requestError.message || "Unable to update enrolment."); }
  };

  return <Shell nav={NAV} active={tab} onNav={setTab} title="Training provider workspace" subtitle="Manage your programmes and enrolments">
    {error && <p className="form-error">{error}</p>}{notice && <p className="toast">{notice}</p>}
    {loading ? <p>Loading provider workspace...</p> : <>
      {tab === "programmes" && <div className="two-grid"><form className="sk-card panel" onSubmit={createProgram}><SectionTitle>Create programme</SectionTitle><input className="sk-input" placeholder="Programme name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /><input className="sk-input" placeholder="Duration" value={form.duration} onChange={(e) => setForm({ ...form, duration: e.target.value })} /><input className="sk-input" placeholder="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /><button className="sk-btn-primary" type="submit">Create programme</button></form><div className="sk-card panel"><SectionTitle>My programmes</SectionTitle>{programs.length ? programs.map((program) => <div className="metric-row" key={program.program_id}><span><b>{program.name}</b><small>{program.duration || "Duration not recorded"} · {program.category || "Uncategorised"}</small></span></div>) : <p className="muted">No programmes created yet.</p>}</div></div>}
      {tab === "enrollments" && <div className="sk-card panel"><SectionTitle>Programme enrolments</SectionTitle>{enrollments.length ? enrollments.map((item) => <div className="metric-row" key={item.enrollment_id}><span><b>{item.trainee_name || `Trainee #${item.trainee_id}`}</b><small>{item.program_name} · Started {item.start_date ? new Date(item.start_date).toLocaleDateString() : "Not recorded"}</small></span><button className="text-button" type="button" onClick={() => changeStatus(item)}><StatusBadge status={item.status} /></button></div>) : <p className="muted">No enrolments exist for your programmes yet.</p>}</div>}
    </>}
  </Shell>;
}
