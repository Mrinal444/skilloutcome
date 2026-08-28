import React,{useState} from "react";
import { Mail, Lock, ArrowLeft } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import AuthShell from "../common/AuthShell.jsx";
import InputField from "../common/InputField.jsx";
import { T } from "../../theme.js";
import { useI18n } from "../../i18n.jsx";

const roleNames={trainee:"Trainee",admin:"Government Admin",employer:"Employer",provider:"Training Provider"};
const rolePaths={trainee:"/trainee",admin:"/admin",employer:"/employer",provider:"/provider"};

export default function LoginScreen(){
  const nav=useNavigate();
  const {role="trainee"}=useParams();
  const {t}=useI18n();
  const [email,setEmail]=useState(""); const [pw,setPw]=useState(""); const [error,setError]=useState("");
  const roleName=roleNames[role]||roleNames.trainee;
  const submit=e=>{e.preventDefault();if(!email||!pw){setError("Please enter email and password.");return;}setError("");nav(rolePaths[role]||"/role");};
  return <AuthShell tagline="Track outcomes. Bridge gaps. Transform lives.">
    <button type="button" className="back-link" onClick={()=>nav("/role")}><ArrowLeft size={14}/> {t.who}</button>
    <form onSubmit={submit}>
      <div style={{fontSize:12,color:T.textDim,marginBottom:8}}>Signing in as</div>
      <div className="sk-card" style={{padding:"10px 12px",marginBottom:18,fontSize:14,fontWeight:600}}>{roleName}</div>
      <h1 className="sk-display" style={{fontSize:26,marginBottom:4,fontWeight:500}}>{t.welcome}</h1>
      <p style={{color:T.textDim,fontSize:13.5,marginBottom:24}}>{t.signinText}</p>
      <InputField icon={Mail} type="email" placeholder="you@organisation.in" value={email} onChange={e=>setEmail(e.target.value)}/>
      <InputField icon={Lock} type="password" placeholder="Password" value={pw} onChange={e=>setPw(e.target.value)}/>
      <div style={{display:"flex",justifyContent:"flex-end",marginBottom:18}}><button type="button" className="text-button" onClick={()=>alert("Password reset link would be sent to your registered email.")}>{t.forgot}</button></div>
      {error&&<p className="form-error">{error}</p>}
      <button type="submit" className="sk-btn-primary" style={{width:"100%",marginBottom:14}}>{t.signin}</button>
      <p style={{fontSize:13,color:T.textDim,textAlign:"center"}}>{t.newHere} <button type="button" className="text-button" onClick={()=>nav(`/register/${role}`)}>{t.create}</button></p>
    </form>
  </AuthShell>;
}
