import React, { useEffect, useMemo, useState } from "react";
import { Award, Briefcase, ClipboardList, Target, TrendingDown, User } from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import Shell from "../common/Shell.jsx";
import SectionTitle from "../common/SectionTitle.jsx";
import StatusBadge from "../common/StatusBadge.jsx";
import ProgressRing from "../common/ProgressRing.jsx";
import SkillGapPanel from "./SkillGapPanel.jsx";
import PlacementPredictionPanel from "./PlacementPredictionPanel.jsx";
import { T } from "../../theme.js";
import { useAuth } from "../../auth/AuthContext.jsx";
import {
  assignTraineeSkills, enrollTrainee, getEmploymentHistory, getFollowupHistory,
  createTrainee, getMyTrainee, getTrainingEnrollments, getTrainingPrograms, updateTrainee,
} from "../../services/api.js";

const NAV = [
  { id: "profile", label: "Profile", icon: User },
  { id: "skills", label: "Skills", icon: Target },
  { id: "training", label: "Training", icon: ClipboardList },
  { id: "employment", label: "Employment", icon: Briefcase },
  { id: "followups", label: "Follow-ups", icon: ClipboardList },
  { id: "progress", label: "Progress", icon: Award },
  { id: "skill-gap", label: "Skill Gap", icon: TrendingDown },
];
const LEVELS = ["BEGINNER", "INTERMEDIATE", "ADVANCED"];
const levelPercent = { BEGINNER: 33, INTERMEDIATE: 66, ADVANCED: 100 };
const label = (value) => String(value || "").replaceAll("_", " ").replace(/\b\w/g, (c) => c.toUpperCase());

function SectionState({ state, empty }) {
  if (state.loading) return <p style={{ color: T.textDim }}>Loading...</p>;
  if (state.error) return <p className="form-error">{state.error}</p>;
  if (!state.items.length) return <p style={{ color: T.textDim }}>{empty}</p>;
  return null;
}

export default function TraineeDashboard() {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const tab = location.pathname.split("/").filter(Boolean)[1] || "profile";
  const [profile, setProfile] = useState(null);
  const [profileForm, setProfileForm] = useState({ education: "", location: "", experience: 0 });
  const [editing, setEditing] = useState(false);
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState({ name: "", level: "BEGINNER" });
  const [programs, setPrograms] = useState([]);
  const [enrollments, setEnrollments] = useState([]);
  const [employment, setEmployment] = useState({ items: [], loading: true, error: "" });
  const [followups, setFollowups] = useState({ items: [], loading: true, error: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const load = async () => {
    setLoading(true); setError("");
    try {
      let trainee;
      try {
        trainee = (await getMyTrainee()).data;
      } catch (requestError) {
        if (requestError.status !== 404) throw requestError;
        trainee = (await createTrainee({ education: "", location: "", experience: 0 })).data;
      }
      setProfile(trainee);
      setProfileForm({ education: trainee.education || "", location: trainee.location || "", experience: trainee.experience || 0 });
      setSkills(trainee.skills || []);
      const [programResponse, enrollmentResponse, employmentResponse, followupResponse] = await Promise.all([
        getTrainingPrograms(), getTrainingEnrollments(trainee.trainee_id),
        getEmploymentHistory(trainee.trainee_id), getFollowupHistory(trainee.trainee_id),
      ]);
      setPrograms(programResponse.data || []); setEnrollments(enrollmentResponse.data || []);
      setEmployment({ items: employmentResponse.data || [], loading: false, error: "" });
      setFollowups({ items: followupResponse.data || [], loading: false, error: "" });
    } catch (requestError) { setError(requestError.message || "Unable to load trainee data."); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);

  const saveProfile = async (event) => {
    event.preventDefault();
    try { await updateTrainee(profile.trainee_id, { ...profileForm, experience: Number(profileForm.experience) }); setEditing(false); setNotice("Profile updated."); await load(); }
    catch (requestError) { setError(requestError.message || "Unable to update profile."); }
  };
  const saveSkill = async (event) => {
    event.preventDefault();
    if (!newSkill.name.trim() || !LEVELS.includes(newSkill.level)) return;
    try { await assignTraineeSkills(profile.trainee_id, [{ name: newSkill.name.trim(), level: newSkill.level }]); setNewSkill({ name: "", level: "BEGINNER" }); setNotice("Skill saved."); await load(); }
    catch (requestError) { setError(requestError.message || "Unable to save skill."); }
  };
  const enroll = async (programId) => {
    try { await enrollTrainee({ trainee_id: profile.trainee_id, program_id: programId }); setNotice("Enrolment submitted."); await load(); }
    catch (requestError) { setError(requestError.message || "Unable to enrol."); }
  };
  const enrolledIds = useMemo(() => new Set(enrollments.map((item) => item.program_id)), [enrollments]);
  const milestones = [
    ["Profile created", Boolean(profile)],
    ["Skills added", skills.length > 0],
    ["Training enrolled", enrollments.length > 0],
    ["Training completed", enrollments.some((item) => item.status === "COMPLETED")],
    ["Employment achieved", employment.items.length > 0],
  ];
  const progress = Math.round((milestones.filter(([, done]) => done).length / milestones.length) * 100);

  return <Shell nav={NAV} active={tab} onNav={(next) => navigate(`/trainee/${next}`)} title={profile?.user_name || user?.name || "Trainee"} subtitle={`${profile?.education || "Trainee"} · ${profile?.location || "Profile pending"}`}>
    {notice && <p className="toast">{notice}</p>}{error && <p className="form-error">{error}</p>}
    {loading ? <p>Loading trainee dashboard...</p> : <>
      {tab === "profile" && <div className="sk-card panel"><SectionTitle action={<button className="text-button" onClick={() => setEditing(!editing)}>{editing ? "Cancel" : "Edit profile"}</button>}>Profile</SectionTitle>{editing ? <form onSubmit={saveProfile}><input className="sk-input" value={profileForm.education} placeholder="Education" onChange={(e) => setProfileForm({ ...profileForm, education: e.target.value })} /><input className="sk-input" value={profileForm.location} placeholder="Location" onChange={(e) => setProfileForm({ ...profileForm, location: e.target.value })} /><input className="sk-input" type="number" min="0" value={profileForm.experience} placeholder="Experience (years)" onChange={(e) => setProfileForm({ ...profileForm, experience: e.target.value })} /><button className="sk-btn-primary" type="submit">Save profile</button></form> : <div><p>{profile?.education || "Education not provided"}</p><p>{profile?.location || "Location not provided"} · {profile?.experience || 0} years experience</p><p style={{ color: T.textDim }}>{profile?.user_email || user?.email}</p></div>}</div>}
      {tab === "skills" && <div className="sk-card panel"><SectionTitle>Skills</SectionTitle><SectionState state={{ loading: false, error: "", items: skills }} empty="No skills added yet." />{skills.map((skill) => <div className="metric-row" key={skill.skill_name}><span>{skill.skill_name}<small>{label(skill.level)}</small></span><span>{levelPercent[skill.level] || 0}%</span></div>)}<form onSubmit={saveSkill} style={{ marginTop: 20 }}><input className="sk-input" placeholder="Skill name" value={newSkill.name} onChange={(e) => setNewSkill({ ...newSkill, name: e.target.value })} required /><select className="sk-input" value={newSkill.level} onChange={(e) => setNewSkill({ ...newSkill, level: e.target.value })}>{LEVELS.map((level) => <option key={level}>{level}</option>)}</select><button className="sk-btn-primary" type="submit">Add or update skill</button></form></div>}
      {tab === "training" && <div className="sk-card panel"><SectionTitle>Available training</SectionTitle><SectionState state={{ loading: false, error: "", items: programs }} empty="No programmes are available." />{programs.map((program) => <div className="metric-row" key={program.program_id}><span><b>{program.name}</b><small>{program.provider} · {program.duration || "Duration not recorded"}</small></span>{enrolledIds.has(program.program_id) ? <StatusBadge status={label(enrollments.find((e) => e.program_id === program.program_id)?.status)} /> : <button className="text-button" onClick={() => enroll(program.program_id)}>Enrol</button>}</div>)}</div>}
      {tab === "employment" && <div className="sk-card panel"><SectionTitle>Employment history</SectionTitle><SectionState state={employment} empty="No employment history yet." />{employment.items.map((item) => <div className="metric-row" key={item.employment_id}><span><b>{item.job_role}</b><small>Employer #{item.employer_id} · Joined {item.joining_date ? new Date(item.joining_date).toLocaleDateString() : "Not recorded"}</small></span><span>{item.salary} · <StatusBadge status={label(item.status)} /></span></div>)}</div>}
      {tab === "followups" && <div className="sk-card panel"><SectionTitle>Follow-up history</SectionTitle><SectionState state={followups} empty="No follow-ups recorded yet." />{followups.items.map((item) => <div className="metric-row" key={item.followup_id}><span><b>{label(item.follow_up_type)}</b><small>{item.feedback || "No remarks"}</small></span><span><StatusBadge status={label(item.status)} /><small>{item.created_at ? new Date(item.created_at).toLocaleDateString() : ""}</small></span></div>)}</div>}
      {tab === "progress" && <div className="sk-card panel"><ProgressRing value={progress} size={120} /><SectionTitle>Journey milestones</SectionTitle>{milestones.map(([name, done]) => <div className="metric-row" key={name}><span>{name}</span><StatusBadge status={done ? "Completed" : "Pending"} /></div>)}</div>}
      {tab === "skill-gap" && <><PlacementPredictionPanel profile={profile} skills={skills} /><SkillGapPanel traineeId={profile?.trainee_id} skills={skills} /></>}
    </>}
  </Shell>;
}
