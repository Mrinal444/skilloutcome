import React from "react";
import { T } from "../../theme.js";

const MAP = {
  Completed: { bg: T.tealSoft, fg: T.teal },
  "In Progress": { bg: "#2A2013", fg: T.amber },
  Placed: { bg: T.tealSoft, fg: T.teal },
  Pending: { bg: T.bgElev2, fg: T.textDim },
};

export default function StatusBadge({ status }) {
  const s = MAP[status] || MAP.Pending;
  return (
    <span style={{ background: s.bg, color: s.fg, fontSize: 11, fontWeight: 600, padding: "3px 9px", borderRadius: 999 }}>
      {status}
    </span>
  );
}
