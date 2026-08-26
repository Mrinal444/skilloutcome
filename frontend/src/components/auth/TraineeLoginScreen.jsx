import React from "react";
import { Mail, Lock, UserRound } from "lucide-react";
import AuthShell from "./AuthShell.jsx";
import InputField from "../common/InputField.jsx";
import { T } from "../../theme.js";

export default function TraineeLoginScreen({ goto }) {
  return (
    <AuthShell tagline="Pick up where you left off." back={() => goto("trainee-choice")}>
      <div className="sk-login-role">TRAINEE PORTAL</div>
      <h1 className="sk-display sk-form-title">Welcome back</h1>
      <p className="sk-form-subtitle">Sign in to continue your skilling and placement journey.</p>
      <InputField icon={Mail} type="email" placeholder="Email address" />
      <InputField icon={Lock} type="password" placeholder="Password" />
      <div className="sk-forgot">Forgot password?</div>
      <button className="sk-btn-primary sk-full" onClick={() => goto("trainee")}>Sign in</button>
      <p className="sk-form-foot">
        New trainee?{" "}
        <button className="sk-inline-link" onClick={() => goto("register")}>Create your profile</button>
      </p>
    </AuthShell>
  );
}
