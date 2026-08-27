import React from "react";
import {
  GraduationCap,
  BarChart3,
  Building2,
  ArrowRight,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import Logo from "../common/Logo.jsx";
import { T } from "../../theme.js";
import { useI18n } from "../../i18n.jsx";

export default function RoleScreen() {
  const navigate = useNavigate();

  const { t } = useI18n();

  /*
   * IMPORTANT:
   *
   * The descriptions now come from i18n.jsx.
   *
   * So when language changes:
   *
   * English
   * ↓
   * हिन्दी
   * ↓
   * ଓଡ଼ିଆ
   *
   * these descriptions change automatically too.
   */
  const roles = [
    {
      id: "trainee",
      label: t.trainee,
      desc:
        t.traineeDesc ||
        "Track your training, skills and placement journey.",
      icon: GraduationCap,
    },

    {
      id: "admin",
      label: t.governmentAdmin,
      desc:
        t.adminDesc ||
        "Monitor outcomes, skill gaps and provider performance.",
      icon: BarChart3,
    },

    {
      id: "employer",
      label: t.employer,
      desc:
        t.employerDesc ||
        "Discover placement-ready trainees by skill and district.",
      icon: Building2,
    },
  ];

  /*
   * Role → Login
   *
   * This preserves your original flow:
   *
   * Who's signing in?
   *       ↓
   * Choose role
   *       ↓
   * /login/trainee
   * /login/admin
   * /login/employer
   */
  const selectRole = (role) => {
    navigate(`/login/${role}`);
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
      }}
    >

      <div
        className="sk-fade"
        style={{
          width: "100%",
          maxWidth: 780,
        }}
      >

        {/* Logo */}
        <Logo />

        {/* Heading */}
        <h1
          className="sk-display"
          style={{
            fontSize: 28,
            margin: "28px 0 6px",
            fontWeight: 500,

            /*
             * MAIN TOPIC WHITE
             */
            color: "#F4EBDE",
          }}
        >
          {t.who}
        </h1>

        {/* Subtitle */}
        <p
          style={{
            color: T.textDim,
            fontSize: 14,
            marginBottom: 28,
          }}
        >
          {t.pick}
        </p>

        {/* =================================================
            ROLE CARDS
        ================================================== */}

        <div className="role-grid">

          {roles.map((role) => {

            const Icon = role.icon;

            return (
              <button
                key={role.id}
                className="sk-card role-card"
                onClick={() =>
                  selectRole(role.id)
                }
              >

                {/* Icon */}
                <span className="role-icon">
                  <Icon size={19} />
                </span>

                {/* Role */}
                <span className="role-label">
                  {role.label}
                </span>

                {/* Description */}
                <span className="role-desc">
                  {role.desc}
                </span>

                {/* Continue */}
                <span className="role-continue">

                  {t.continue}

                  <ArrowRight
                    size={13}
                  />

                </span>

              </button>
            );
          })}

        </div>

      </div>
    </div>
  );
}