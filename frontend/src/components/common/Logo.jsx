import React from "react";
import { T } from "../../theme.js";

export default function Logo({ size = 34 }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div
        className="sk-display"
        style={{
          width: size,
          height: size,
          borderRadius: 10,
          background: T.tealSoft,
          border: `1px solid ${T.tealDeep}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: T.teal,
          fontWeight: 700,
          fontSize: size * 0.42,
        }}
      >
        SI
      </div>
      <span className="sk-display" style={{ fontSize: 18, fontWeight: 600, color: T.text }}>
        Skillimpact
      </span>
    </div>
  );
}
