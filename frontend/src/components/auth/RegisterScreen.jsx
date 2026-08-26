import React from "react";
import { User, Mail, Lock } from "lucide-react";
import AuthShell from "./AuthShell.jsx";
import InputField from "../common/InputField.jsx";

export default function RegisterScreen({ goto }) {
  return (
    <AuthShell tagline="Start your journey." back={() => goto("trainee-choice")}>
      <div className="sk-login-role">NEW TRAINEE</div>
      <h1 className="sk-display sk-form-title">Create your profile</h1>
      <p className="sk-form-subtitle">Set up your trainee account to begin tracking your outcomes.</p>
      <InputField icon={User} placeholder="Full name" />
      <InputField icon={Mail} type="email" placeholder="Email address" />
      <InputField icon={Lock} type="password" placeholder="Create password" />
      <InputField icon={Lock} type="password" placeholder="Confirm password" />
      <button className="sk-btn-primary sk-full" onClick={() => goto("trainee")}>Create profile</button>
      <p className="sk-form-foot">
        Already registered?{" "}
        <button className="sk-inline-link" onClick={() => goto("trainee-login")}>Sign in</button>
      </p>
    </AuthShell>
  );
}
