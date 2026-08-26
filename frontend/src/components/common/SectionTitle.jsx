import React from "react";
import { T } from "../../theme.js";

export default function SectionTitle({ children, action }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
      <h3 style={{ fontSize: 14.5, fontWeight: 600, color: T.text }}>{children}</h3>
      {action && <span style={{ fontSize: 12, color: T.textFaint }}>{action}</span>}
    </div>
  );
}
