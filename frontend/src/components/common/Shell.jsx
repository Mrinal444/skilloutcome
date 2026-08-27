import React, { useState } from "react";
import {
  Search,
  Bell,
  Settings,
  LogOut,
  X,
  Menu,
  Globe,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import Logo from "./Logo.jsx";
import { useI18n } from "../../i18n.jsx";

export default function Shell({
  nav,
  active,
  onNav,
  title,
  subtitle,
  children,
}) {
  const navigate = useNavigate();

  const {
    t,
    lang,
    setLang,
    languages,
  } = useI18n();

  const [mobile, setMobile] = useState(false);
  const [notice, setNotice] = useState(false);
  const [settings, setSettings] = useState(false);
  const [query, setQuery] = useState("");

  /*
   * Search sidebar items
   */
  const filtered = nav.filter((item) =>
    item.label
      ?.toLowerCase()
      .includes(query.toLowerCase())
  );

  /*
   * Navigation
   */
  const choose = (id) => {
    onNav(id);
    setMobile(false);
  };

  /*
   * Language change
   *
   * This changes the global language through I18nProvider.
   * Every component using useI18n() will re-render automatically.
   */
  const changeLanguage = (newLang) => {
    setLang(newLang);
  };

  return (
    <div className="shell">

      {/* =====================================================
          SIDEBAR
      ====================================================== */}

      <aside
        className={`sidebar ${
          mobile ? "open" : ""
        }`}
      >

        <div className="sidebar-top">
          <Logo size={30} />

          <button
            className="icon-btn mobile-close"
            onClick={() => setMobile(false)}
            aria-label={t.close}
          >
            <X size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">

          {filtered.map((item) => {

            /*
             * Section headings such as:
             * ENGAGEMENT
             * OUTCOMES
             * INTELLIGENCE
             */
            if (item.section) {
              return (
                <div
                  key={item.id}
                  className="nav-section"
                >
                  {item.label}
                </div>
              );
            }

            const Icon = item.icon;

            return (
              <button
                key={item.id}
                className={`sk-nav-item ${
                  active === item.id
                    ? "active"
                    : ""
                }`}
                onClick={() =>
                  choose(item.id)
                }
              >
                <Icon size={16} />

                <span>
                  {item.label}
                </span>
              </button>
            );
          })}

        </nav>

        {/* =================================================
            SIDEBAR BOTTOM
        ================================================== */}

        <div className="sidebar-bottom">

          <button
            className="sk-nav-item"
            onClick={() =>
              setSettings(true)
            }
          >
            <Settings size={16} />

            <span>
              {t.settings}
            </span>
          </button>

          <button
            className="sk-nav-item"
            onClick={() =>
              navigate("/login")
            }
          >
            <LogOut size={16} />

            <span>
              {t.signout}
            </span>
          </button>

        </div>
      </aside>

      {/* Mobile overlay */}
      {mobile && (
        <div
          className="sidebar-overlay"
          onClick={() =>
            setMobile(false)
          }
        />
      )}

      {/* =====================================================
          MAIN
      ====================================================== */}

      <main className="sk-scroll shell-main">

        {/* =================================================
            HEADER
        ================================================== */}

        <header className="shell-header">

          <div className="header-left">

            <button
              className="icon-btn mobile-menu"
              onClick={() =>
                setMobile(true)
              }
              aria-label="Menu"
            >
              <Menu size={19} />
            </button>

            <div>

              <h2 className="sk-display header-title">
                {title}
              </h2>

              {subtitle && (
                <p className="header-subtitle">
                  {subtitle}
                </p>
              )}

            </div>

          </div>

          {/* =================================================
              HEADER ACTIONS
          ================================================== */}

          <div className="header-actions">

            {/* Search */}
            <div className="search-box">

              <Search size={14} />

              <input
                value={query}
                onChange={(e) =>
                  setQuery(e.target.value)
                }
                placeholder={t.search}
                aria-label={t.search}
              />

            </div>

            {/* Language */}
            <div className="language-box">

              <Globe size={15} />

              <select
                value={lang}
                onChange={(e) =>
                  changeLanguage(
                    e.target.value
                  )
                }
                aria-label="Language"
              >
                {languages.map(
                  ([id, name]) => (
                    <option
                      key={id}
                      value={id}
                    >
                      {name}
                    </option>
                  )
                )}
              </select>

            </div>

            {/* Notifications */}
            <button
              className="icon-btn"
              onClick={() =>
                setNotice(
                  (value) => !value
                )
              }
              aria-label={
                t.notifications ||
                "Notifications"
              }
            >
              <Bell size={17} />

              {notice && (
                <span className="notification-dot" />
              )}
            </button>

            {/* Profile */}
            <button
              className="avatar"
              onClick={() =>
                setSettings(true)
              }
              aria-label={t.settings}
            >
              RP
            </button>

          </div>
        </header>

        {/* =================================================
            NOTIFICATION POPUP
        ================================================== */}

        {notice && (
          <div className="notice-pop">

            <strong>
              {t.notifications ||
                "Notifications"}
            </strong>

            <p>
              {t.verificationNotification ||
                "3 verification records need review."}
            </p>

            <button
              className="text-button"
              onClick={() => {
                setNotice(false);
                choose("verification");
              }}
            >
              {t.reviewNow ||
                "Review now"}
            </button>

          </div>
        )}

        {/* =================================================
            PAGE CONTENT
        ================================================== */}

        <div className="shell-content sk-fade">
          {children}
        </div>

      </main>

      {/* =====================================================
          SETTINGS MODAL
      ====================================================== */}

      {settings && (
        <div
          className="modal-backdrop"
          onClick={() =>
            setSettings(false)
          }
        >

          <div
            className="modal sk-card"
            onClick={(e) =>
              e.stopPropagation()
            }
          >

            <div className="modal-head">

              <h3>
                {t.settings}
              </h3>

              <button
                className="icon-btn"
                onClick={() =>
                  setSettings(false)
                }
                aria-label={t.close}
              >
                <X size={17} />
              </button>

            </div>

            <p>
              {t.dashboardPreferences ||
                "Dashboard preferences"}
            </p>

            {/* Language */}
            <label>

              {t.language ||
                "Language"}

              <select
                value={lang}
                onChange={(e) =>
                  changeLanguage(
                    e.target.value
                  )
                }
              >
                {languages.map(
                  ([id, name]) => (
                    <option
                      key={id}
                      value={id}
                    >
                      {name}
                    </option>
                  )
                )}
              </select>

            </label>

            <button
              className="sk-btn-primary"
              onClick={() =>
                setSettings(false)
              }
            >
              {t.save}
            </button>

          </div>
        </div>
      )}

    </div>
  );
}