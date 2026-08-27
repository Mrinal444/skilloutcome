import React from "react";
import Logo from "../common/Logo.jsx";
import ThreadIllustration from "../common/ThreadIllustration.jsx";
import {T} from "../../theme.js";
import {useI18n} from "../../i18n.jsx";
export default function AuthShell({children,tagline}){const {lang,setLang,languages}=useI18n();return <div className="auth-shell"><div className="auth-brand"><Logo/><div><p className="sk-display auth-tagline">{tagline}</p><p className="auth-copy">Every trainee's path from enrollment to placement, mapped as one continuous thread.</p></div><div className="auth-illustration"><ThreadIllustration/></div></div><div className="auth-panel"><div className="auth-language"><span>🌐</span><select value={lang} onChange={e=>setLang(e.target.value)}>{languages.map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></div><div className="auth-content sk-fade">{children}</div></div></div>}
