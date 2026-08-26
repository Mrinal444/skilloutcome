import React from "react";
import { ArrowRight, ShieldCheck, GraduationCap } from "lucide-react";
import Logo from "../common/Logo.jsx";
import { T } from "../../theme.js";

export default function WelcomeScreen({ goto }) {
  return (
    <main className="sk-welcome">
      <header className="sk-portal-header">
        <Logo />
        <div className="sk-portal-actions">
          <button className="sk-top-choice" onClick={() => goto("trainee-choice")}>
            <GraduationCap size={15} /> Trainee
          </button>
          <button className="sk-top-choice admin" onClick={() => goto("admin-login")}>
            <ShieldCheck size={15} /> Admin
          </button>
        </div>
      </header>

      <section className="sk-welcome-content sk-fade">
        <span className="sk-eyebrow">SKILLING OUTCOME PLATFORM</span>
        <h1 className="sk-display sk-welcome-title">
          From learning<br />to meaningful work.
        </h1>
        <p className="sk-welcome-copy">
          Skillimpact connects training, skills, assessment and employment
          outcomes in one continuous journey.
        </p>

        <div className="sk-welcome-grid">
          <button className="sk-entry-card" onClick={() => goto("trainee-choice")}>
            <div className="sk-entry-icon"><GraduationCap size={21} /></div>
            <div>
              <span className="sk-entry-kicker">FOR LEARNERS</span>
              <h2 className="sk-display">I'm a trainee</h2>
              <p>Track training, skills, assessment and your placement journey.</p>
              <span className="sk-entry-link">Continue <ArrowRight size={14} /></span>
            </div>
          </button>

          <button className="sk-entry-card" onClick={() => goto("admin-login")}>
            <div className="sk-entry-icon"><ShieldCheck size={21} /></div>
            <div>
              <span className="sk-entry-kicker">FOR PROGRAMME TEAMS</span>
              <h2 className="sk-display">I'm an admin</h2>
              <p>Monitor outcomes, skill gaps, placement and provider performance.</p>
              <span className="sk-entry-link">Admin sign in <ArrowRight size={14} /></span>
            </div>
          </button>
        </div>

        <p className="sk-welcome-note">
          Choose your role to continue. You can return here anytime.
        </p>
      </section>
    </main>
  );
}
