import React from "react";
import { Search, Bell, Settings, LogOut } from "lucide-react";
import Logo from "./Logo.jsx";
import { T } from "../../theme.js";

export default function Shell({ nav, active, onNav, title, subtitle, children }) {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "230px 1fr", minHeight: "100vh" }}>
      <aside style={{ background: T.bgElev, borderRight: `1px solid ${T.border}`, padding: "20px 14px", display: "flex", flexDirection: "column" }}>
        <div style={{ padding: "0 6px 22px" }}>
          <Logo size={30} />
        </div>
        <nav style={{ display: "flex", flexDirection: "column", gap: 3 }}>
          {nav.map((item) => (
            <div key={item.id} className={`sk-nav-item${active === item.id ? " active" : ""}`} onClick={() => onNav(item.id)}>
              <item.icon size={16} />
              {item.label}
            </div>
          ))}
        </nav>
        <div style={{ marginTop: "auto", paddingTop: 18, borderTop: `1px solid ${T.borderSoft}` }}>
          <div className="sk-nav-item">
            <Settings size={16} /> Settings
          </div>
          <div className="sk-nav-item">
            <LogOut size={16} /> Sign out
          </div>
        </div>
      </aside>
      <main className="sk-scroll" style={{ overflowY: "auto", height: "100vh" }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            padding: "18px 28px",
            borderBottom: `1px solid ${T.borderSoft}`,
            position: "sticky",
            top: 0,
            background: "rgba(18,15,11,0.9)",
            backdropFilter: "blur(6px)",
            zIndex: 10,
          }}
        >
          <div>
            <h2 className="sk-display" style={{ fontSize: 20, fontWeight: 500 }}>
              {title}
            </h2>
            {subtitle && <p style={{ fontSize: 12.5, color: T.textDim, marginTop: 2 }}>{subtitle}</p>}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{ position: "relative" }}>
              <Search size={14} color={T.textFaint} style={{ position: "absolute", left: 10, top: 9 }} />
              <input
                placeholder="Search"
                style={{
                  background: T.bgElev2,
                  border: `1px solid ${T.border}`,
                  borderRadius: 8,
                  padding: "7px 10px 7px 30px",
                  fontSize: 12.5,
                  color: T.text,
                  width: 180,
                  outline: "none",
                }}
              />
            </div>
            <Bell size={17} color={T.textDim} style={{ cursor: "pointer" }} />
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: "50%",
                background: T.taupe,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 12,
                fontWeight: 600,
                color: "#241C13",
              }}
            >
              RP
            </div>
          </div>
        </div>
        <div style={{ padding: 28 }} className="sk-fade">
          {children}
        </div>
      </main>
    </div>
  );
}
