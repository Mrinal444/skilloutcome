import React from "react";
import { TrendingUp } from "lucide-react";
import { T } from "../../theme.js";

export default function StatCard({ label, value, delta, icon: Icon }) {
  return (
    <div className="sk-card" style={{ padding: "16px 18px", flex: 1, minWidth: 0 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
        <span style={{ fontSize: 12.5, color: T.textDim }}>{label}</span>
        {Icon && <Icon size={15} color={T.taupe} />}
      </div>
      <p className="sk-mono" style={{ fontSize: 22, fontWeight: 500, color: T.text, marginBottom: 6 }}>
        {value}
      </p>
      {delta && (
        <span style={{ fontSize: 11.5, color: T.teal, display: "flex", alignItems: "center", gap: 3 }}>
          <TrendingUp size={11} /> {delta}
        </span>
      )}
    </div>
  );
}
