import React from "react";
import { Mail, Lock, ShieldCheck } from "lucide-react";
import AuthShell from "./AuthShell.jsx";
import InputField from "../common/InputField.jsx";

export default function AdminLoginScreen({ goto }) {
  return (
    <AuthShell tagline="See the bigger picture." back={() => goto("welcome")}>
      <div className="sk-login-role"><ShieldCheck size={13} /> PROGRAMME ADMIN</div>
      <h1 className="sk-display sk-form-title">Admin sign in</h1>
      <p className="sk-form-subtitle">
        Access programme outcomes, skill-gap and provider analytics.
      </p>
      <InputField icon={Mail} type="email" placeholder="Official organisation email" />
      <InputField icon={Lock} type="password" placeholder="Password" />
      <div className="sk-forgot">Forgot password?</div>
      <button className="sk-btn-primary sk-full" onClick={() => goto("admin")}>Sign in</button>
      <p className="sk-security-note">Authorised programme personnel only.</p>
    </AuthShell>
  );
}
