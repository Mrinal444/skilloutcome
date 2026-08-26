import React, { useState } from "react";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, RadialBarChart, RadialBar, PolarAngleAxis,
} from "recharts";
import {
  Home, Users, BarChart3, Award, Briefcase, TrendingUp, CheckCircle2, Clock,
  Search, Bell, ChevronRight, User, Lock, Mail, GraduationCap, Target,
  FileText, Building2, ArrowRight, MapPin, Eye, EyeOff, Settings, LogOut,
  ClipboardList, Sparkles,
} from "lucide-react";

const T = {
  bg: "#120F0B",
  bgElev: "#1B1712",
  bgElev2: "#231C15",
  border: "#332A20",
  borderSoft: "#241D16",
  text: "#F4EBDE",
  textDim: "#B9AA97",
  textFaint: "#7C7062",
  teal: "#00C9AD",
  tealDeep: "#0A3E37",
  tealSoft: "#0F2C27",
  taupe: "#96806D",
  tan: "#CDB5A1",
  cream: "#FFEBCD",
  amber: "#E3A45E",
  danger: "#D9736B",
};

const FONTS = `
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
* { box-sizing: border-box; }
.sk-root { background:${T.bg}; color:${T.text}; font-family:'Inter',sans-serif; min-height:100vh; }
.sk-display { font-family:'Fraunces',serif; letter-spacing:-0.01em; }
.sk-mono { font-family:'JetBrains Mono',monospace; }
.sk-scroll::-webkit-scrollbar{width:6px;height:6px;}
.sk-scroll::-webkit-scrollbar-thumb{background:${T.border};border-radius:4px;}
.sk-fade{animation:skfade .5s ease both;}
@keyframes skfade{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}
.sk-thread{stroke-dasharray:6 5;animation:skdash 6s linear infinite;}
@media (prefers-reduced-motion:reduce){.sk-thread{animation:none;}}
@keyframes skdash{to{stroke-dashoffset:-220;}}
.sk-input{width:100%;background:${T.bgElev2};border:1px solid ${T.border};border-radius:10px;padding:12px 14px 12px 40px;color:${T.text};font-size:14px;outline:none;transition:border-color .15s;}
.sk-input:focus{border-color:${T.teal};}
.sk-input::placeholder{color:${T.textFaint};}
.sk-btn-primary{background:${T.teal};color:#062420;font-weight:600;border:none;border-radius:10px;padding:12px 18px;font-size:14px;cursor:pointer;transition:filter .15s, transform .1s;}
.sk-btn-primary:hover{filter:brightness(1.08);}
.sk-btn-primary:active{transform:scale(0.98);}
.sk-btn-ghost{background:transparent;color:${T.textDim};border:1px solid ${T.border};border-radius:10px;padding:11px 18px;font-size:14px;cursor:pointer;transition:border-color .15s, color .15s;}
.sk-btn-ghost:hover{border-color:${T.taupe};color:${T.text};}
.sk-card{background:${T.bgElev};border:1px solid ${T.border};border-radius:16px;}
.sk-nav-item{display:flex;align-items:center;gap:10px;padding:10px 14px;border-radius:10px;color:${T.textDim};font-size:13.5px;cursor:pointer;transition:background .15s,color .15s;border:1px solid transparent;}
.sk-nav-item:hover{background:${T.bgElev2};color:${T.text};}
.sk-nav-item.active{background:${T.tealSoft};color:${T.teal};border-color:${T.tealDeep};}
.sk-pill-switch{position:fixed;top:16px;right:16px;display:flex;gap:4px;background:${T.bgElev};border:1px solid ${T.border};border-radius:999px;padding:4px;z-index:50;}
.sk-pill-switch button{background:transparent;border:none;color:${T.textFaint};font-size:11px;padding:6px 10px;border-radius:999px;cursor:pointer;font-family:'Inter',sans-serif;}
.sk-pill-switch button.active{background:${T.teal};color:#062420;font-weight:600;}
`;

function InputField({ icon: Icon, type = "text", placeholder, value, onChange }) {
  const [show, setShow] = useState(false);
  const isPw = type === "password";
  return (
    <div style={{ position: "relative", marginBottom: 14 }}>
      <Icon size={16} color={T.textFaint} style={{ position: "absolute", left: 14, top: 14 }} />
      <input
        className="sk-input"
        type={isPw && show ? "text" : type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        style={isPw ? { paddingRight: 40 } : undefined}
      />
      {isPw && (
        <button
          onClick={() => setShow((s) => !s)}
          aria-label="Toggle password visibility"
          style={{ position: "absolute", right: 12, top: 11, background: "none", border: "none", cursor: "pointer" }}
        >
          {show ? <EyeOff size={16} color={T.textFaint} /> : <Eye size={16} color={T.textFaint} />}
        </button>
      )}
    </div>
  );
}

function Logo({ size = 34 }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div style={{
        width: size, height: size, borderRadius: 10, background: T.tealSoft,
        border: `1px solid ${T.tealDeep}`, display: "flex", alignItems: "center",
        justifyContent: "center", color: T.teal, fontWeight: 700, fontSize: size * 0.42,
      }} className="sk-display">SI</div>
      <span className="sk-display" style={{ fontSize: 18, fontWeight: 600, color: T.text }}>Skillimpact</span>
    </div>
  );
}

function ThreadIllustration() {
  const stages = ["Enrolled", "Trained", "Assessed", "Placed"];
  return (
    <svg viewBox="0 0 320 420" width="100%" height="100%" style={{ maxWidth: 300 }}>
      <path d="M40 40 C 160 40, 40 150, 160 150 S 280 260, 160 260 S 40 370, 160 380"
        fill="none" stroke={T.tealDeep} strokeWidth="2" />
      <path d="M40 40 C 160 40, 40 150, 160 150 S 280 260, 160 260 S 40 370, 160 380"
        fill="none" stroke={T.teal} strokeWidth="2" className="sk-thread" opacity="0.8" />
      {[{x:40,y:40},{x:160,y:150},{x:160,y:260},{x:160,y:380}].map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="6" fill={T.bg} stroke={T.teal} strokeWidth="2" />
          <text x={p.x + 16} y={p.y + 4} fill={T.textDim} fontSize="12" fontFamily="Inter">{stages[i]}</text>
        </g>
      ))}
    </svg>
  );
}

function AuthShell({ children, tagline }) {
  return (
    <div style={{ minHeight: "100vh", display: "grid", gridTemplateColumns: "1fr 1fr" }}>
      <div style={{
        background: T.bgElev, borderRight: `1px solid ${T.border}`, padding: 48,
        display: "flex", flexDirection: "column", justifyContent: "space-between",
      }}>
        <Logo />
        <div>
          <p className="sk-display" style={{ fontSize: 32, lineHeight: 1.15, maxWidth: 380, color: T.text, fontWeight: 500 }}>
            {tagline}
          </p>
          <p style={{ color: T.textDim, fontSize: 14, marginTop: 12, maxWidth: 360 }}>
            Every trainee's path from enrollment to placement, mapped as one continuous thread.
          </p>
        </div>
        <div style={{ display: "flex", justifyContent: "center" }}>
          <ThreadIllustration />
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 32 }}>
        <div style={{ width: "100%", maxWidth: 360 }} className="sk-fade">{children}</div>
      </div>
    </div>
  );
}

function LoginScreen({ goto }) {
  return (
    <AuthShell tagline="Track outcomes. Bridge gaps. Transform lives.">
      <h1 className="sk-display" style={{ fontSize: 26, marginBottom: 4, fontWeight: 500 }}>Welcome back</h1>
      <p style={{ color: T.textDim, fontSize: 13.5, marginBottom: 24 }}>Sign in to continue tracking your skilling outcomes.</p>
      <InputField icon={Mail} type="email" placeholder="you@organisation.in" />
      <InputField icon={Lock} type="password" placeholder="Password" />
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 18 }}>
        <span style={{ fontSize: 12.5, color: T.teal, cursor: "pointer" }}>Forgot password?</span>
      </div>
      <button className="sk-btn-primary" style={{ width: "100%", marginBottom: 14 }} onClick={() => goto("role")}>
        Sign in
      </button>
      <p style={{ fontSize: 13, color: T.textDim, textAlign: "center" }}>
        New here?{" "}
        <span style={{ color: T.teal, cursor: "pointer", fontWeight: 500 }} onClick={() => goto("register")}>
          Create an account
        </span>
      </p>
    </AuthShell>
  );
}

function RegisterScreen({ goto }) {
  return (
    <AuthShell tagline="Measure. Empower. Improve.">
      <h1 className="sk-display" style={{ fontSize: 26, marginBottom: 4, fontWeight: 500 }}>Create your account</h1>
      <p style={{ color: T.textDim, fontSize: 13.5, marginBottom: 24 }}>Join the network tracking real skilling outcomes.</p>
      <InputField icon={User} placeholder="Full name" />
      <InputField icon={Mail} type="email" placeholder="you@organisation.in" />
      <InputField icon={Lock} type="password" placeholder="Password" />
      <InputField icon={Lock} type="password" placeholder="Confirm password" />
      <button className="sk-btn-primary" style={{ width: "100%", margin: "10px 0 14px" }} onClick={() => goto("role")}>
        Create account
      </button>
      <p style={{ fontSize: 13, color: T.textDim, textAlign: "center" }}>
        Already have an account?{" "}
        <span style={{ color: T.teal, cursor: "pointer", fontWeight: 500 }} onClick={() => goto("login")}>
          Sign in
        </span>
      </p>
    </AuthShell>
  );
}

function RoleScreen({ goto }) {
  const roles = [
    { id: "trainee", label: "Trainee", desc: "Track your training, skills and placement journey.", icon: GraduationCap, go: "trainee" },
    { id: "admin", label: "Programme admin", desc: "Monitor outcomes, skill gaps and provider performance.", icon: BarChart3, go: "admin" },
    { id: "employer", label: "Employer", desc: "Discover placement-ready trainees by skill and district.", icon: Building2, go: "trainee" },
  ];
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div className="sk-fade" style={{ width: "100%", maxWidth: 780 }}>
        <div style={{ marginBottom: 8 }}><Logo /></div>
        <h1 className="sk-display" style={{ fontSize: 28, margin: "28px 0 6px", fontWeight: 500 }}>Who's signing in?</h1>
        <p style={{ color: T.textDim, fontSize: 14, marginBottom: 28 }}>Pick a role to see the dashboard built for it.</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
          {roles.map((r) => (
            <div
              key={r.id}
              onClick={() => goto(r.go)}
              className="sk-card"
              style={{ padding: 22, cursor: "pointer", transition: "border-color .15s, transform .1s" }}
              onMouseEnter={(e) => (e.currentTarget.style.borderColor = T.teal)}
              onMouseLeave={(e) => (e.currentTarget.style.borderColor = T.border)}
            >
              <div style={{ width: 40, height: 40, borderRadius: 10, background: T.tealSoft, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 16 }}>
                <r.icon size={19} color={T.teal} />
              </div>
              <p style={{ fontWeight: 600, fontSize: 15, marginBottom: 6 }}>{r.label}</p>
              <p style={{ fontSize: 12.5, color: T.textDim, lineHeight: 1.5 }}>{r.desc}</p>
              <div style={{ display: "flex", alignItems: "center", gap: 4, marginTop: 16, fontSize: 12.5, color: T.teal, fontWeight: 500 }}>
                Continue <ArrowRight size={13} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, delta, icon: Icon }) {
  return (
    <div className="sk-card" style={{ padding: "16px 18px", flex: 1, minWidth: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
        <span style={{ fontSize: 12.5, color: T.textDim }}>{label}</span>
        {Icon && <Icon size={15} color={T.taupe} />}
      </div>
      <p className="sk-mono" style={{ fontSize: 22, fontWeight: 500, color: T.text, marginBottom: 6 }}>{value}</p>
      {delta && (
        <span style={{ fontSize: 11.5, color: T.teal, display: "flex", alignItems: "center", gap: 3 }}>
          <TrendingUp size={11} /> {delta}
        </span>
      )}
    </div>
  );
}

function SectionTitle({ children, action }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
      <h3 style={{ fontSize: 14.5, fontWeight: 600, color: T.text }}>{children}</h3>
      {action && <span style={{ fontSize: 12, color: T.textFaint }}>{action}</span>}
    </div>
  );
}

function Shell({ nav, active, onNav, title, subtitle, children }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "230px 1fr", minHeight: "100vh" }}>
      <aside style={{ background: T.bgElev, borderRight: `1px solid ${T.border}`, padding: "20px 14px", display: "flex", flexDirection: "column" }}>
        <div style={{ padding: "0 6px 22px" }}><Logo size={30} /></div>
        <nav style={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {nav.map((item) => (
            <div key={item.id} className={`sk-nav-item${active === item.id ? " active" : ""}`} onClick={() => onNav(item.id)}>
              <item.icon size={16} />
              {item.label}
            </div>
          ))}
        </nav>
        <div style={{ marginTop: "auto", paddingTop: 18, borderTop: `1px solid ${T.borderSoft}` }}>
          <div className="sk-nav-item"><Settings size={16} /> Settings</div>
          <div className="sk-nav-item"><LogOut size={16} /> Sign out</div>
        </div>
      </aside>
      <main className="sk-scroll" style={{ overflowY: "auto", height: "100vh" }}>
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          padding: "18px 28px", borderBottom: `1px solid ${T.borderSoft}`, position: "sticky", top: 0,
          background: "rgba(18,15,11,0.9)", backdropFilter: "blur(6px)", zIndex: 10,
        }}>
          <div>
            <h2 className="sk-display" style={{ fontSize: 20, fontWeight: 500 }}>{title}</h2>
            {subtitle && <p style={{ fontSize: 12.5, color: T.textDim, marginTop: 2 }}>{subtitle}</p>}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ position: "relative" }}>
              <Search size={14} color={T.textFaint} style={{ position: "absolute", left: 10, top: 9 }} />
              <input placeholder="Search" style={{
                background: T.bgElev2, border: `1px solid ${T.border}`, borderRadius: 8,
                padding: "7px 10px 7px 30px", fontSize: 12.5, color: T.text, width: 180, outline: "none",
              }} />
            </div>
            <Bell size={17} color={T.textDim} style={{ cursor: "pointer" }} />
            <div style={{ width: 32, height: 32, borderRadius: "50%", background: T.taupe, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 600, color: "#241C13" }}>RP</div>
          </div>
        </div>
        <div style={{ padding: 28 }} className="sk-fade">{children}</div>
      </main>
    </div>
  );
}

function ProgressRing({ value, size = 96 }) {
  const data = [{ value, fill: T.teal }];
  return (
    <div style={{ width: size, height: size, position: "relative" }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart innerRadius="72%" outerRadius="100%" data={data} startAngle={90} endAngle={-270}>
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar background={{ fill: T.bgElev2 }} dataKey="value" cornerRadius={20} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column" }}>
        <span className="sk-mono" style={{ fontSize: 18, fontWeight: 500 }}>{value}%</span>
      </div>
    </div>
  );
}

function SkillBar({ name, level, target }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
        <span style={{ fontSize: 13, color: T.text }}>{name}</span>
        <span className="sk-mono" style={{ fontSize: 12, color: T.textDim }}>{level}%</span>
      </div>
      <div style={{ height: 7, background: T.bgElev2, borderRadius: 4, position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${level}%`, background: T.teal, borderRadius: 4 }} />
        <div style={{ position: "absolute", left: `${target}%`, top: -2, bottom: -2, width: 2, background: T.tan }} />
      </div>
    </div>
  );
}

function StatusBadge({ status }) {
  const map = {
    Completed: { bg: T.tealSoft, fg: T.teal },
    "In Progress": { bg: "#2A2013", fg: T.amber },
    Placed: { bg: T.tealSoft, fg: T.teal },
    Pending: { bg: T.bgElev2, fg: T.textDim },
  };
  const s = map[status] || map.Pending;
  return (
    <span style={{ background: s.bg, color: s.fg, fontSize: 11, fontWeight: 600, padding: "3px 9px", borderRadius: 999 }}>
      {status}
    </span>
  );
}

const traineeNav = [
  { id: "profile", label: "Profile", icon: User },
  { id: "skills", label: "Skills", icon: Target },
  { id: "training", label: "Training history", icon: ClipboardList },
  { id: "employment", label: "Employment", icon: Briefcase },
  { id: "progress", label: "Progress", icon: Award },
];

function TraineeDashboard({ goto }) {
  const [tab, setTab] = useState("profile");
  const skills = [
    { name: "Python", level: 82, target: 90 },
    { name: "SQL", level: 74, target: 80 },
    { name: "Data analysis", level: 68, target: 85 },
    { name: "Communication", level: 90, target: 80 },
    { name: "AWS", level: 55, target: 75 },
  ];
  const training = [
    { name: "Advanced Java Development", status: "Completed", date: "Mar 2024" },
    { name: "AWS Cloud Practitioner", status: "In Progress", date: "Started Jun 2025" },
    { name: "Communication Skills Bootcamp", status: "Completed", date: "Jan 2024" },
    { name: "Data Analysis Fundamentals", status: "Completed", date: "Nov 2023" },
  ];
  const salaryTrend = [
    { m: "Jun", v: 22000 }, { m: "Aug", v: 24000 }, { m: "Oct", v: 25500 },
    { m: "Dec", v: 26800 }, { m: "Feb", v: 28000 },
  ];
  const milestones = [
    { label: "Enrolled", done: true, date: "Oct 2023" },
    { label: "Training completed", done: true, date: "Feb 2024" },
    { label: "Assessment cleared", done: true, date: "Mar 2024" },
    { label: "Placed", done: true, date: "Jun 2024" },
    { label: "6-month retention", done: false, date: "In progress" },
  ];

  return (
    <Shell nav={traineeNav} active={tab} onNav={setTab} title="Rohit Patil" subtitle="Trainee · TRN/2024/56098 · Pune, Maharashtra">
      {tab === "profile" && (
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1fr", gap: 20 }}>
          <div className="sk-card" style={{ padding: 22 }}>
            <SectionTitle>Current employment</SectionTitle>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", rowGap: 14, fontSize: 13 }}>
              {[["Company", "Tech Mahindra"], ["Role", "Software Associate"], ["Joined", "12 Jun 2024"],
                ["Monthly salary", "\u20B928,000"], ["Type", "Full time"], ["Location", "Pune"]].map(([k, v]) => (
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
                  <div style={{
                    position: "absolute", left: -18, top: 2, width: 10, height: 10, borderRadius: "50%",
                    background: m.done ? T.teal : T.bgElev2, border: `2px solid ${m.done ? T.teal : T.border}`,
                  }} />
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
            <SectionTitle action="Teal = current · tan mark = programme target">Skill levels</SectionTitle>
            {skills.map((s) => <SkillBar key={s.name} {...s} />)}
          </div>
          <div className="sk-card" style={{ padding: 22, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <ProgressRing value={74} size={110} />
            <p style={{ fontSize: 13, color: T.textDim, marginTop: 14, textAlign: "center" }}>Average skill readiness against programme targets</p>
          </div>
        </div>
      )}

      {tab === "training" && (
        <div className="sk-card" style={{ padding: 22 }}>
          <SectionTitle>Training history</SectionTitle>
          {training.map((t, i) => (
            <div key={i} style={{
              display: "flex", justifyContent: "space-between", alignItems: "center",
              padding: "14px 0", borderBottom: i < training.length - 1 ? `1px solid ${T.borderSoft}` : "none",
            }}>
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
                <p style={{ fontSize: 14, fontWeight: 500 }}>Tech Mahindra</p>
                <p style={{ fontSize: 12, color: T.textDim }}>Software Associate · Full time</p>
              </div>
              <div style={{ marginLeft: "auto" }}><StatusBadge status="Placed" /></div>
            </div>
            <p style={{ fontSize: 12, color: T.textFaint }}>Retained 12 months on the job, 6-month retention milestone cleared.</p>
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

const adminNav = [
  { id: "overview", label: "Overview", icon: Home },
  { id: "placement", label: "Placement analytics", icon: BarChart3 },
  { id: "skillgap", label: "Skill gap analysis", icon: Target },
  { id: "provider", label: "Provider performance", icon: FileText },
  { id: "district", label: "District analysis", icon: MapPin },
];

function AdminDashboard() {
  const [tab, setTab] = useState("overview");
  const trend = [
    { m: "Jan", rate: 58 }, { m: "Feb", rate: 61 }, { m: "Mar", rate: 65 },
    { m: "Apr", rate: 68 }, { m: "May", rate: 70 }, { m: "Jun", rate: 72 },
  ];
  const skillGaps = [
    { skill: "Python", demand: 82, proficiency: 61 },
    { skill: "SQL", demand: 68, proficiency: 54 },
    { skill: "Data analysis", demand: 61, proficiency: 47 },
    { skill: "AWS", demand: 55, proficiency: 33 },
    { skill: "Excel", demand: 40, proficiency: 58 },
  ];
  const providers = [
    { name: "TechSkill Academy", rate: 81 },
    { name: "Digital Bridge", rate: 74 },
    { name: "NextGen IT", rate: 76 },
    { name: "Rural Skill Mission", rate: 69 },
    { name: "CraftWorks", rate: 63 },
  ];
  const districts = [
    { name: "Pune", rate: 78 },
    { name: "Nagpur", rate: 71 },
    { name: "Nashik", rate: 66 },
    { name: "Aurangabad", rate: 60 },
    { name: "Kolhapur", rate: 58 },
  ];

  return (
    <Shell nav={adminNav} active={tab} onNav={setTab} title="Programme overview" subtitle="1 Jan 2025 \u2013 31 May 2025">
      {tab === "overview" && (
        <>
          <div style={{ display: "flex", gap: 16, marginBottom: 22, flexWrap: "wrap" }}>
            <StatCard label="Total trainees" value="10,000" delta="+12.4% vs last period" icon={Users} />
            <StatCard label="Placed" value="7,200" delta="+15.2% vs last period" icon={CheckCircle2} />
            <StatCard label="Retention (6 mo)" value="82%" delta="+6.1% vs last period" icon={Award} />
            <StatCard label="Avg salary" value="\u20B94.8 LPA" delta="+8.6% vs last period" icon={TrendingUp} />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20 }}>
            <div className="sk-card" style={{ padding: 22 }}>
              <SectionTitle action="Monthly">Placement rate trend</SectionTitle>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={trend}>
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
                    <span className="sk-mono" style={{ fontSize: 11.5, color: T.textDim }}>{s.demand}%</span>
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
            <LineChart data={trend}>
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

export default function App() {
  const [screen, setScreen] = useState("login");
  const goto = (s) => setScreen(s);

  return (
    <div className="sk-root">
      <style>{FONTS}</style>
      <div className="sk-pill-switch">
        {["login", "register", "role", "trainee", "admin"].map((s) => (
          <button key={s} className={screen === s ? "active" : ""} onClick={() => setScreen(s)}>
            {s}
          </button>
        ))}
      </div>
      {screen === "login" && <LoginScreen goto={goto} />}
      {screen === "register" && <RegisterScreen goto={goto} />}
      {screen === "role" && <RoleScreen goto={goto} />}
      {screen === "trainee" && <TraineeDashboard goto={goto} />}
      {screen === "admin" && <AdminDashboard />}
    </div>
  );
}
