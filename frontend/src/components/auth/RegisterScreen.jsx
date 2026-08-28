import React,{useState} from "react";
import {User,Mail,Lock,ArrowLeft} from "lucide-react";
import {useNavigate,useParams} from "react-router-dom";
import AuthShell from "../common/AuthShell.jsx";
import InputField from "../common/InputField.jsx";
import {T} from "../../theme.js";
import {useI18n} from "../../i18n.jsx";

const roleNames={trainee:"Trainee",admin:"Government Admin",employer:"Employer",provider:"Training Provider"};
export default function RegisterScreen(){
 const nav=useNavigate();const {role="trainee"}=useParams();const {t}=useI18n();
 const [form,setForm]=useState({name:"",email:"",pw:"",confirm:""});const [err,setErr]=useState("");
 const update=k=>e=>setForm({...form,[k]:e.target.value});
 const submit=e=>{e.preventDefault();if(!form.name||!form.email||!form.pw||!form.confirm){setErr("Please complete all fields.");return;}if(form.pw!==form.confirm){setErr("Passwords do not match.");return;}nav(`/login/${role}`)};
 return <AuthShell tagline="Measure. Empower. Improve.">
  <button type="button" className="back-link" onClick={()=>nav(`/login/${role}`)}><ArrowLeft size={14}/> {t.signin}</button>
  <form onSubmit={submit}>
   <div style={{fontSize:12,color:T.textDim,marginBottom:8}}>Creating account for</div>
   <div className="sk-card" style={{padding:"10px 12px",marginBottom:18,fontSize:14,fontWeight:600}}>{roleNames[role]||roleNames.trainee}</div>
   <h1 className="sk-display" style={{fontSize:26,marginBottom:4,fontWeight:500}}>{t.registerTitle}</h1>
   <p style={{color:T.textDim,fontSize:13.5,marginBottom:24}}>{t.registerText}</p>
   <InputField icon={User} placeholder="Full name" value={form.name} onChange={update("name")}/>
   <InputField icon={Mail} type="email" placeholder="you@organisation.in" value={form.email} onChange={update("email")}/>
   <InputField icon={Lock} type="password" placeholder="Password" value={form.pw} onChange={update("pw")}/>
   <InputField icon={Lock} type="password" placeholder="Confirm password" value={form.confirm} onChange={update("confirm")}/>
   {err&&<p className="form-error">{err}</p>}
   <button className="sk-btn-primary" style={{width:"100%",margin:"10px 0 14px"}} type="submit">{t.registerTitle}</button>
  </form>
 </AuthShell>;
}
