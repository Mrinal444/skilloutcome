import React, { useEffect, useMemo, useState } from "react";
import { Building2, BriefcaseBusiness, Users, X } from "lucide-react";
import Shell from "../common/Shell.jsx";
import SectionTitle from "../common/SectionTitle.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import {
  createEmployer,
  createEmploymentRecord,
  getAllTrainees,
  getMyEmployer,
  getMyEmploymentRecords,
  updateEmployer,
  updateEmploymentRecord,
} from "../../services/api.js";

const NAV = [
  { id: "company", label: "Company profile", icon: Building2 },
  { id: "trainees", label: "Trainees", icon: Users },
  { id: "outcomes", label: "Employment outcomes", icon: BriefcaseBusiness },
];

const emptyCompany = { company_name: "", industry: "", location: "" };
const emptyOutcome = { trainee_id: "", job_role: "", salary: "", status: "EMPLOYED" };

export default function EmployerDashboard() {
  const [tab, setTab] = useState("company");
  const [company, setCompany] = useState(null);
  const [companyForm, setCompanyForm] = useState(emptyCompany);
  const [trainees, setTrainees] = useState([]);
  const [records, setRecords] = useState([]);
  const [outcome, setOutcome] = useState(emptyOutcome);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const [employerResponse, traineeResponse, recordResponse] = await Promise.all([
        getMyEmployer().catch((requestError) => requestError.message === "Employer profile not found" ? { data: null } : Promise.reject(requestError)),
        getAllTrainees(),
        getMyEmploymentRecords(),
      ]);
      setCompany(employerResponse.data || null);
      setCompanyForm(employerResponse.data || emptyCompany);
      setTrainees(traineeResponse.data || []);
      setRecords(recordResponse.data || []);
    } catch (requestError) {
      setError(requestError.message || "Unable to load employer workspace.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filteredTrainees = useMemo(() => trainees.filter((trainee) =>
    [trainee.user_name, trainee.user_email, trainee.location, ...(trainee.skills || []).map((skill) => skill.skill_name)]
      .filter(Boolean).some((value) => value.toLowerCase().includes(query.toLowerCase()))
  ), [trainees, query]);

  const saveCompany = async (event) => {
    event.preventDefault();
    setError("");
    try {
      const response = company
        ? await updateEmployer(company.employer_id, companyForm)
        : await createEmployer(companyForm);
      setCompany(response.data);
      setCompanyForm(response.data);
      setEditing(false);
      setNotice("Company profile saved.");
    } catch (requestError) { setError(requestError.message || "Unable to save company profile."); }
  };

  const saveOutcome = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await createEmploymentRecord({
        ...outcome,
        trainee_id: Number(outcome.trainee_id),
        employer_id: company.employer_id,
        salary: Number(outcome.salary),
      });
      setOutcome(emptyOutcome);
      setNotice("Employment outcome recorded.");
      const response = await getMyEmploymentRecords();
      setRecords(response.data || []);
    } catch (requestError) { setError(requestError.message || "Unable to record employment outcome."); }
  };

  const updateRecord = async (record) => {
    const status = window.prompt("Status: EMPLOYED, RESIGNED, or TERMINATED", record.status);
    if (!status || !["EMPLOYED", "RESIGNED", "TERMINATED"].includes(status.toUpperCase())) return;
    try {
      await updateEmploymentRecord(record.employment_id, { status: status.toUpperCase() });
      setNotice("Employment record updated.");
      const response = await getMyEmploymentRecords();
      setRecords(response.data || []);
    } catch (requestError) { setError(requestError.message || "Unable to update employment record."); }
  };

  return <Shell nav={NAV} active={tab} onNav={setTab} title="Employer workspace" subtitle="Employment verification and outcome reporting">
    {error && <p className="form-error">{error}</p>}
    {notice && <p className="toast">{notice}</p>}
    {loading ? <p>Loading employer workspace...</p> : <>
      {tab === "company" && <form className="sk-card panel" onSubmit={saveCompany}>
        <SectionTitle action={company && <button className="text-button" type="button" onClick={() => setEditing(true)}>Edit profile</button>}>Company profile</SectionTitle>
        {!company || editing ? <><input className="sk-input" placeholder="Company name" value={companyForm.company_name} onChange={(e) => setCompanyForm({ ...companyForm, company_name: e.target.value })} required /><input className="sk-input" placeholder="Industry" value={companyForm.industry || ""} onChange={(e) => setCompanyForm({ ...companyForm, industry: e.target.value })} /><input className="sk-input" placeholder="City / district" value={companyForm.location || ""} onChange={(e) => setCompanyForm({ ...companyForm, location: e.target.value })} /><button className="sk-btn-primary" type="submit">Save company</button></> : <p><b>{company.company_name}</b><br />{company.industry || "Industry not recorded"} · {company.location || "Location not recorded"}</p>}
      </form>}
      {tab === "trainees" && <div className="sk-card panel"><div className="page-head"><SectionTitle>Placement-ready trainees</SectionTitle><input className="sk-input" placeholder="Search name, skill, or location" value={query} onChange={(e) => setQuery(e.target.value)} /></div><div className="table-wrap"><table><thead><tr><th>Name</th><th>Skills</th><th>Education</th><th>Location</th><th>Action</th></tr></thead><tbody>{filteredTrainees.map((trainee) => <tr key={trainee.trainee_id}><td><b>{trainee.user_name}</b><small>TRN/{trainee.trainee_id}</small></td><td>{(trainee.skills || []).map((skill) => skill.skill_name).join(", ") || "Not recorded"}</td><td>{trainee.education || "Not recorded"}</td><td>{trainee.location || "Not recorded"}</td><td><button className="text-button" type="button" onClick={() => setSelected(trainee)}>View</button></td></tr>)}</tbody></table></div>{!filteredTrainees.length && <p className="muted">No trainees match your search.</p>}</div>}
      {tab === "outcomes" && <div className="sk-card panel"><SectionTitle>Employment outcomes</SectionTitle><form onSubmit={saveOutcome}><select className="sk-input" value={outcome.trainee_id} onChange={(e) => setOutcome({ ...outcome, trainee_id: e.target.value })} required><option value="">Select trainee</option>{trainees.map((trainee) => <option key={trainee.trainee_id} value={trainee.trainee_id}>{trainee.user_name} — TRN/{trainee.trainee_id}</option>)}</select><input className="sk-input" placeholder="Job role" value={outcome.job_role} onChange={(e) => setOutcome({ ...outcome, job_role: e.target.value })} required /><input className="sk-input" type="number" min="0" placeholder="Salary" value={outcome.salary} onChange={(e) => setOutcome({ ...outcome, salary: e.target.value })} required /><button className="sk-btn-primary" type="submit" disabled={!company}>Record outcome</button></form><div style={{ marginTop: 24 }}>{records.length ? records.map((record) => <div key={record.employment_id} className="metric-row"><span><b>{record.job_role}</b><small>Trainee #{record.trainee_id} · ₹{Number(record.salary).toLocaleString()}</small></span><button className="text-button" type="button" onClick={() => updateRecord(record)}><StatusBadge status={record.status} /></button></div>) : <p className="muted">No employment records created by your company yet.</p>}</div></div>}
    </>}
    {selected && <div className="modal-backdrop" onClick={() => setSelected(null)}><div className="sk-card simple-card" onClick={(event) => event.stopPropagation()}><button className="icon-btn" type="button" onClick={() => setSelected(null)}><X size={16} /></button><SectionTitle>Candidate details</SectionTitle><Info label="Name" value={selected.user_name} /><Info label="Email" value={selected.user_email} /><Info label="Education" value={selected.education} /><Info label="Location" value={selected.location} /><Info label="Skills" value={(selected.skills || []).map((skill) => `${skill.skill_name} (${skill.level})`).join(", ") || "Not recorded"} /></div></div>}
  </Shell>;
}

function Info({ label, value }) { return <p><span className="muted">{label}</span><br /><b>{value || "Not recorded"}</b></p>; }
