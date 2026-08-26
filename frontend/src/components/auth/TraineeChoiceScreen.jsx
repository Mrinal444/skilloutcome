import React from "react";
import { ArrowLeft, ArrowRight, LogIn, UserPlus, GraduationCap } from "lucide-react";
import Logo from "../common/Logo.jsx";

export default function TraineeChoiceScreen({ goto }) {
  return (
    <main className="sk-choice-page">
      <header className="sk-portal-header">
        <Logo />
        <button className="sk-back-link" onClick={() => goto("welcome")}>
          <ArrowLeft size={15} /> Back
        </button>
      </header>

      <section className="sk-choice-content sk-fade">
        <span className="sk-eyebrow">TRAINEE PORTAL</span>
        <div className="sk-choice-icon"><GraduationCap size={22} /></div>
        <h1 className="sk-display">Are you a new or existing trainee?</h1>
        <p>Choose the path that matches your training status.</p>

        <div className="sk-choice-grid">
          <button className="sk-choice-card" onClick={() => goto("register")}>
            <div className="sk-choice-card-icon"><UserPlus size={20} /></div>
            <h2 className="sk-display">I'm a new trainee</h2>
            <p>Create your Skillimpact profile and start your skilling journey.</p>
            <span className="sk-entry-link">Create profile <ArrowRight size={14} /></span>
          </button>

          <button className="sk-choice-card" onClick={() => goto("trainee-login")}>
            <div className="sk-choice-card-icon"><LogIn size={20} /></div>
            <h2 className="sk-display">I'm an existing trainee</h2>
            <p>Sign in to continue tracking your training and employment outcomes.</p>
            <span className="sk-entry-link">Trainee sign in <ArrowRight size={14} /></span>
          </button>
        </div>
      </section>
    </main>
  );
}
