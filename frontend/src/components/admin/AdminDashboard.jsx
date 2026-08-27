import React, { useMemo, useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

import {
  Home,
  Users,
  RefreshCw,
  MessageSquare,
  PhoneCall,
  BarChart3,
  IndianRupee,
  Target,
  UserX,
  BookOpen,
  Building2,
  MapPin,
  UsersRound,
  CheckCircle2,
  FileText,
  Download,
  Search,
  ChevronRight,
} from "lucide-react";

import Shell from "../common/Shell.jsx";
import SectionTitle from "../common/SectionTitle.jsx";
import StatCard from "../common/StatCard.jsx";
import { T } from "../../theme.js";
import {
  stats,
  placementTrend,
  skillGaps,
  providers,
  districts,
} from "../../data/admin.js";
import { useI18n } from "../../i18n.jsx";

const ICON = {
  overview: Home,
  trainees: Users,
  followups: PhoneCall,
  messages: MessageSquare,
  placement: BarChart3,
  wage: IndianRupee,
  skillgap: Target,
  nonplacement: UserX,
  course: BookOpen,
  providers: Building2,
  district: MapPin,
  demographic: UsersRound,
  verification: CheckCircle2,
  reports: FileText,
};

const trainees = [
  "Aarav Sharma",
  "Priya Das",
  "Rohan Patil",
  "Sneha Mohanty",
  "Vikram Singh",
  "Ananya Rao",
  "Kunal Verma",
  "Meera Nair",
];

export default function AdminDashboard() {
  const { t } = useI18n();

  const [tab, setTab] = useState("overview");
  const [refresh, setRefresh] = useState(0);
  const [traineeSearch, setTraineeSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [toast, setToast] = useState("");

  /*
   * Sidebar
   */
  const nav = useMemo(
    () => [
      {
        id: "overview",
        label: t.overview,
        icon: ICON.overview,
      },
      {
        id: "trainees",
        label: t.trainees,
        icon: ICON.trainees,
      },

      {
        id: "engagement",
        label: t.engagement,
        section: true,
      },
      {
        id: "followups",
        label: t.followups,
        icon: ICON.followups,
      },
      {
        id: "messages",
        label: t.messages,
        icon: ICON.messages,
      },

      {
        id: "outcomes",
        label: t.outcomes,
        section: true,
      },
      {
        id: "placement",
        label: t.placement,
        icon: ICON.placement,
      },
      {
        id: "wage",
        label: t.wage,
        icon: ICON.wage,
      },

      {
        id: "intelligence",
        label: t.intelligence,
        section: true,
      },
      {
        id: "skillgap",
        label: t.skillgap,
        icon: ICON.skillgap,
      },
      {
        id: "nonplacement",
        label: t.nonplacement,
        icon: ICON.nonplacement,
      },

      {
        id: "performance",
        label: t.performance,
        section: true,
      },
      {
        id: "course",
        label: t.course,
        icon: ICON.course,
      },
      {
        id: "providers",
        label: t.providers,
        icon: ICON.providers,
      },
      {
        id: "district",
        label: t.district,
        icon: ICON.district,
      },
      {
        id: "demographic",
        label: t.demographic,
        icon: ICON.demographic,
      },

      {
        id: "quality",
        label: t.quality,
        section: true,
      },
      {
        id: "verification",
        label: t.verification,
        icon: ICON.verification,
      },

      {
        id: "reports",
        label: t.reports,
        icon: ICON.reports,
      },
    ],
    [t]
  );

  /*
   * Toast
   */
  const notify = (message) => {
    setToast(message);

    setTimeout(() => {
      setToast("");
    }, 2200);
  };

  /*
   * Export report
   */
  const exportReport = () => {
    const report = [
      "SkillImpact Government Admin Report",
      "",
      `${t.totalTrainees}: 10,000`,
      `${t.placed}: 7,200`,
      `${t.retention}: 82%`,
      `${t.salary}: ₹4.8 LPA`,
    ].join("\n");

    const blob = new Blob([report], {
      type: "text/plain",
    });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "skillimpact-report.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(url);

    notify(t.reportExported || t.export);
  };

  /*
   * Page title
   */
  const titleMap = {
    overview: t.adminTitle,
    trainees: t.trainees,
    followups: t.followups,
    messages: t.messages,
    placement: t.placement,
    wage: t.wage,
    skillgap: t.skillgap,
    nonplacement: t.nonplacement,
    course: t.course,
    providers: t.providers,
    district: t.district,
    demographic: t.demographic,
    verification: t.verification,
    reports: t.reports,
  };

  /*
   * Trainee search
   */
  const filtered = trainees.filter((name) =>
    name.toLowerCase().includes(traineeSearch.toLowerCase())
  );

  return (
    <Shell
      nav={nav}
      active={tab}
      onNav={setTab}
      title={titleMap[tab] || t.adminTitle}
      subtitle={t.period}
    >
      {/* =========================
          TOP TOOLBAR
      ========================== */}
      <div className="admin-toolbar">
        <div>
          <p className="eyebrow">
            {t.governmentProgramme || "GOVERNMENT PROGRAMME"}
          </p>

          <h1 className="sk-display admin-heading">
            {titleMap[tab] || t.adminTitle}
          </h1>
        </div>

        <div className="toolbar-actions">
          <button
            className="sk-btn-ghost"
            onClick={() => {
              setRefresh((value) => value + 1);
              notify(t.dashboardRefreshed || t.refresh);
            }}
          >
            <RefreshCw size={14} />
            {t.refresh}
          </button>

          <button
            className="sk-btn-primary"
            onClick={exportReport}
          >
            <Download size={14} />
            {t.export}
          </button>
        </div>
      </div>

      {/* =========================
          TOAST
      ========================== */}
      {toast && <div className="toast">{toast}</div>}

      {/* =========================
          OVERVIEW
      ========================== */}
      {tab === "overview" && (
        <Overview
          t={t}
          refresh={refresh}
          onOpen={setTab}
        />
      )}

      {/* =========================
          TRAINEES
      ========================== */}
      {tab === "trainees" && (
        <TraineePage
          t={t}
          data={filtered}
          search={traineeSearch}
          setSearch={setTraineeSearch}
          onSelect={setSelected}
        />
      )}

      {/* =========================
          PLACEMENT
      ========================== */}
      {tab === "placement" && <Placement t={t} />}

      {/* =========================
          WAGE
      ========================== */}
      {tab === "wage" && <Wage t={t} />}

      {/* =========================
          SKILL GAP
      ========================== */}
      {tab === "skillgap" && <SkillGap t={t} />}

      {/* =========================
          PROVIDERS
      ========================== */}
      {tab === "providers" && <ProviderPage t={t} />}

      {/* =========================
          DISTRICT
      ========================== */}
      {tab === "district" && <DistrictPage t={t} />}

      {/* =========================
          COURSE
      ========================== */}
      {tab === "course" && (
        <SimpleAnalytics
          title={t.coursePerformance}
          rows={[
            t.advancedJava,
            t.cloudPractitioner,
            t.dataAnalytics,
            t.digitalMarketing,
            t.communicationSkills,
          ]}
          t={t}
        />
      )}

      {/* =========================
          DEMOGRAPHIC
      ========================== */}
      {tab === "demographic" && (
        <SimpleAnalytics
          title={t.demographicPerformance}
          rows={[
            t.age18to24,
            t.age25to34,
            t.age35to44,
            t.women,
            t.ruralTrainees,
          ]}
          t={t}
        />
      )}

      {/* =========================
          FOLLOW UPS
      ========================== */}
      {tab === "followups" && (
        <ActionPage
          t={t}
          title={t.followups}
          items={[
            t.followupItem1,
            t.followupItem2,
            t.followupItem3,
          ]}
          action={t.markReviewed}
          onAction={() =>
            notify(t.followupReviewed)
          }
        />
      )}

      {/* =========================
          MESSAGES
      ========================== */}
      {tab === "messages" && (
        <ActionPage
          t={t}
          title={t.messages}
          items={[
            t.messageItem1,
            t.messageItem2,
            t.messageItem3,
          ]}
          action={t.reply}
          onAction={() =>
            notify(t.replyOpened)
          }
        />
      )}

      {/* =========================
          NON PLACEMENT
      ========================== */}
      {tab === "nonplacement" && (
        <ActionPage
          t={t}
          title={t.nonplacement}
          items={[
            t.nonplacementItem1,
            t.nonplacementItem2,
            t.nonplacementItem3,
          ]}
          action={t.createIntervention}
          onAction={() =>
            notify(t.interventionCreated)
          }
        />
      )}

      {/* =========================
          VERIFICATION
      ========================== */}
      {tab === "verification" && (
        <Verification
          t={t}
          notify={notify}
        />
      )}

      {/* =========================
          REPORTS
      ========================== */}
      {tab === "reports" && (
        <Reports
          t={t}
          exportReport={exportReport}
        />
      )}

      {/* =========================
          TRAINEE MODAL
      ========================== */}
      {selected && (
        <div
          className="modal-backdrop"
          onClick={() => setSelected(null)}
        >
          <div
            className="modal sk-card"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="modal-head">
              <h3>{selected}</h3>

              <button
                className="icon-btn"
                onClick={() =>
                  setSelected(null)
                }
              >
                ×
              </button>
            </div>

            <p>
              {t.traineeRecord}
            </p>

            <div className="detail-grid">
              <span>{t.trainingStatus}</span>
              <b>{t.completed}</b>

              <span>{t.placementLabel}</span>
              <b>{t.placed}</b>

              <span>{t.district}</span>
              <b>Pune</b>

              <span>{t.verification}</span>
              <b>{t.verified}</b>
            </div>

            <button
              className="sk-btn-primary"
              onClick={() => {
                setSelected(null);
                notify(t.recordOpened);
              }}
            >
              {t.open}
            </button>
          </div>
        </div>
      )}
    </Shell>
  );
}


/* =========================================================
   OVERVIEW
========================================================= */

function Overview({ t, onOpen }) {
  return (
    <>
      <div className="stat-grid">
        {stats.map((stat, index) => (
          <StatCard
            key={stat.label}
            {...stat}
            icon={
              [
                Users,
                CheckCircle2,
                Target,
                IndianRupee,
              ][index]
            }
          />
        ))}
      </div>

      <div className="overview-grid">
        {/* Placement trend */}
        <div className="sk-card panel">
          <SectionTitle action={t.period}>
            {t.placementTrend}
          </SectionTitle>

          <ResponsiveContainer
            width="100%"
            height={250}
          >
            <LineChart data={placementTrend}>
              <CartesianGrid
                stroke={T.borderSoft}
                vertical={false}
              />

              <XAxis
                dataKey="m"
                stroke={T.textFaint}
                fontSize={11}
                tickLine={false}
                axisLine={false}
              />

              <YAxis
                stroke={T.textFaint}
                fontSize={11}
                tickLine={false}
                axisLine={false}
                unit="%"
              />

              <Tooltip
                contentStyle={{
                  background: T.bgElev2,
                  border: `1px solid ${T.border}`,
                  fontSize: 12,
                  borderRadius: 8,
                }}
              />

              <Line
                type="monotone"
                dataKey="rate"
                stroke={T.teal}
                strokeWidth={2.5}
                dot={{
                  r: 3,
                  fill: T.teal,
                }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Skill demand */}
        <div className="sk-card panel">
          <SectionTitle>
            {t.demand}
          </SectionTitle>

          {skillGaps.map((skill) => (
            <div
              key={skill.skill}
              className="skill-row"
            >
              <div>
                <span>{skill.skill}</span>

                <small>
                  {skill.proficiency}%{" "}
                  {t.proficiency || "proficiency"} ·{" "}
                  {skill.demand}%{" "}
                  {t.demandLabel || "demand"}
                </small>
              </div>

              <b>{skill.demand}%</b>

              <div className="mini-bar">
                <i
                  style={{
                    width: `${skill.demand}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Insights */}
      <div className="three-grid">
        <Insight
          title={t.placementPipeline}
          value="72%"
          text={t.placementPipelineText}
          onClick={() => onOpen("placement")}
          t={t}
        />

        <Insight
          title={t.skillGapAlert}
          value="AWS"
          text={t.skillGapAlertText}
          onClick={() => onOpen("skillgap")}
          t={t}
        />

        <Insight
          title={t.dataQuality}
          value="96.8%"
          text={t.dataQualityText}
          onClick={() => onOpen("verification")}
          t={t}
        />
      </div>
    </>
  );
}


/* =========================================================
   INSIGHT CARD
========================================================= */

function Insight({
  title,
  value,
  text,
  onClick,
  t,
}) {
  return (
    <button
      className="sk-card insight-card"
      onClick={onClick}
    >
      <span>{title}</span>

      <strong>{value}</strong>

      <p>{text}</p>

      <small>
        {t.openAnalysis}
        <ChevronRight size={13} />
      </small>
    </button>
  );
}


/* =========================================================
   TRAINEES
========================================================= */

function TraineePage({
  t,
  data,
  search,
  setSearch,
  onSelect,
}) {
  return (
    <div className="sk-card panel">
      <div className="page-head">
        <SectionTitle>
          {t.trainees}
        </SectionTitle>

        <div className="table-search">
          <Search size={14} />

          <input
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
            placeholder={t.searchTrainees}
          />
        </div>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{t.name}</th>
              <th>{t.training}</th>
              <th>{t.placementLabel}</th>
              <th>{t.district}</th>
              <th>{t.verification}</th>
              <th>{t.action}</th>
            </tr>
          </thead>

          <tbody>
            {data.map((name, index) => (
              <tr key={name}>
                <td>
                  <b>{name}</b>

                  <small>
                    TRN/2025/{56000 + index}
                  </small>
                </td>

                <td>
                  {t.completed}
                </td>

                <td>
                  <span className="status good">
                    {t.placed}
                  </span>
                </td>

                <td>
                  {
                    districts[
                      index % districts.length
                    ].name
                  }
                </td>

                <td>
                  <span className="status good">
                    {t.verified}
                  </span>
                </td>

                <td>
                  <button
                    className="text-button"
                    onClick={() =>
                      onSelect(name)
                    }
                  >
                    {t.open}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {!data.length && (
          <div className="empty">
            {t.noResults}
          </div>
        )}
      </div>
    </div>
  );
}


/* =========================================================
   PLACEMENT
========================================================= */

function Placement({ t }) {
  return (
    <div className="sk-card panel">
      <SectionTitle
        action={t.programmeTrend}
      >
        {t.placement}
      </SectionTitle>

      <ResponsiveContainer
        width="100%"
        height={360}
      >
        <LineChart data={placementTrend}>
          <CartesianGrid
            stroke={T.borderSoft}
            vertical={false}
          />

          <XAxis
            dataKey="m"
            stroke={T.textFaint}
          />

          <YAxis
            unit="%"
            stroke={T.textFaint}
          />

          <Tooltip
            contentStyle={{
              background: T.bgElev2,
              border: `1px solid ${T.border}`,
            }}
          />

          <Line
            dataKey="rate"
            type="monotone"
            stroke={T.teal}
            strokeWidth={3}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}


/* =========================================================
   WAGE
========================================================= */

function Wage({ t }) {
  return (
    <div className="two-grid">
      <div className="sk-card panel">
        <SectionTitle>
          {t.salaryProgression}
        </SectionTitle>

        <ResponsiveContainer
          width="100%"
          height={300}
        >
          <BarChart
            data={[
              {
                m: "2023",
                v: 3.4,
              },
              {
                m: "2024",
                v: 4.1,
              },
              {
                m: "2025",
                v: 4.8,
              },
            ]}
          >
            <CartesianGrid
              stroke={T.borderSoft}
              vertical={false}
            />

            <XAxis
              dataKey="m"
              stroke={T.textFaint}
            />

            <YAxis
              unit=" LPA"
              stroke={T.textFaint}
            />

            <Tooltip />

            <Bar
              dataKey="v"
              fill={T.teal}
              radius={[6, 6, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="sk-card panel">
        <SectionTitle>
          {t.retention}
        </SectionTitle>

        <div className="big-number">
          82%
        </div>

        <p className="muted">
          {t.retentionDescription}
        </p>

        <div className="progress-line">
          <i
            style={{
              width: "82%",
            }}
          />
        </div>

        <p className="muted">
          {t.retentionImprovement}
        </p>
      </div>
    </div>
  );
}


/* =========================================================
   SKILL GAP
========================================================= */

function SkillGap({ t }) {
  return (
    <div className="sk-card panel">
      <SectionTitle>
        {t.skillgap}
      </SectionTitle>

      {skillGaps.map((skill) => (
        <div
          className="gap-row"
          key={skill.skill}
        >
          <div>
            <b>{skill.skill}</b>

            <span>
              {t.demandLabel}{" "}
              {skill.demand}% ·{" "}
              {t.proficiency}{" "}
              {skill.proficiency}%
            </span>
          </div>

          <div className="gap-bars">
            <i
              style={{
                width: `${skill.demand}%`,
              }}
            />

            <i
              style={{
                width: `${skill.proficiency}%`,
              }}
            />
          </div>

          <strong>
            {skill.demand -
              skill.proficiency}{" "}
            pts
          </strong>
        </div>
      ))}
    </div>
  );
}


/* =========================================================
   PROVIDERS
========================================================= */

function ProviderPage({ t }) {
  return (
    <div className="sk-card panel">
      <SectionTitle>
        {t.providerPerformance}
      </SectionTitle>

      <div className="provider-list">
        {providers.map((provider) => (
          <div
            className="provider-row"
            key={provider.name}
          >
            <div>
              <b>{provider.name}</b>

              <small>
                {t.placementRate}
              </small>
            </div>

            <strong>
              {provider.rate}%
            </strong>

            <div className="progress-line">
              <i
                style={{
                  width: `${provider.rate}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


/* =========================================================
   DISTRICT
========================================================= */

function DistrictPage({ t }) {
  return (
    <div className="sk-card panel">
      <SectionTitle>
        {t.districtPerformance}
      </SectionTitle>

      <div className="district-grid">
        {districts.map((district) => (
          <div
            className="district-card"
            key={district.name}
          >
            <span>
              {district.name}
            </span>

            <strong>
              {district.rate}%
            </strong>

            <div className="progress-line">
              <i
                style={{
                  width: `${district.rate}%`,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


/* =========================================================
   SIMPLE ANALYTICS
========================================================= */

function SimpleAnalytics({
  title,
  rows,
  t,
}) {
  return (
    <div className="sk-card panel">
      <SectionTitle>
        {title}
      </SectionTitle>

      {rows.map((row, index) => {
        const value =
          82 - index * 4;

        return (
          <div
            className="metric-row"
            key={row}
          >
            <span>{row}</span>

            <b>{value}%</b>

            <div className="progress-line">
              <i
                style={{
                  width: `${value}%`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}


/* =========================================================
   ACTION PAGE
========================================================= */

function ActionPage({
  title,
  items,
  action,
  onAction,
}) {
  return (
    <div className="sk-card panel">
      <SectionTitle>
        {title}
      </SectionTitle>

      {items.map((item) => (
        <div
          className="action-row"
          key={item}
        >
          <span>{item}</span>

          <button
            className="sk-btn-ghost"
            onClick={onAction}
          >
            {action}
          </button>
        </div>
      ))}
    </div>
  );
}


/* =========================================================
   VERIFICATION
========================================================= */

function Verification({
  t,
  notify,
}) {
  const [items, setItems] = useState([
    "TRN/2025/7812 · Aadhaar match",
    "TRN/2025/8110 · Training certificate",
    "TRN/2025/9002 · Placement proof",
  ]);

  const verify = (item) => {
    setItems((current) =>
      current.filter(
        (value) => value !== item
      )
    );

    notify(t.recordVerified);
  };

  return (
    <div className="sk-card panel">
      <SectionTitle>
        {t.verificationQueue}
      </SectionTitle>

      {items.map((item) => (
        <div
          className="action-row"
          key={item}
        >
          <span>{item}</span>

          <div>
            <span className="status pending">
              {t.pending}
            </span>

            <button
              className="text-button"
              onClick={() =>
                verify(item)
              }
            >
              {t.verified}
            </button>
          </div>
        </div>
      ))}

      {!items.length && (
        <div className="empty">
          {t.verificationClear}
        </div>
      )}
    </div>
  );
}


/* =========================================================
   REPORTS
========================================================= */

function Reports({
  t,
  exportReport,
}) {
  return (
    <div className="three-grid">
      <Insight
        title={t.monthlyOutcomeReport}
        value="PDF"
        text={t.monthlyOutcomeText}
        onClick={exportReport}
        t={t}
      />

      <Insight
        title={t.districtReport}
        value="CSV"
        text={t.districtReportText}
        onClick={exportReport}
        t={t}
      />

      <Insight
        title={t.providerScorecard}
        value="XLS"
        text={t.providerScorecardText}
        onClick={exportReport}
        t={t}
      />
    </div>
  );
}