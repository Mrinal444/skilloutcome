import React from "react";
import { ArrowLeft } from "lucide-react";
import Logo from "../common/Logo.jsx";
import ThreadIllustration from "../common/ThreadIllustration.jsx";

export default function AuthShell({ children, tagline, back }) {
  return (
    <div className="sk-auth-shell">
      <section className="sk-auth-visual">
        <Logo />
        <div className="sk-auth-copy">
          <p className="sk-display">{tagline}</p>
          <p>Every trainee's path from enrollment to placement, mapped as one continuous thread.</p>
        </div>
        <div className="sk-thread-wrap"><ThreadIllustration /></div>
      </section>

      <section className="sk-auth-form-area">
        <div className="sk-auth-form sk-fade">
          {back && (
            <button className="sk-back-link sk-auth-back" onClick={back}>
              <ArrowLeft size={15} /> Back
            </button>
          )}
          {children}
        </div>
      </section>
    </div>
  );
}
