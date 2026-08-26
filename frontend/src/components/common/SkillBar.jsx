import React from "react";
import { T } from "../../theme.js";

export default function SkillBar({ name, level, target }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
        <span style={{ fontSize: 13, color: T.text }}>{name}</span>
        <span className="sk-mono" style={{ fontSize: 12, color: T.textDim }}>
          {level}%
        </span>
      </div>
      <div style={{ height: 7, background: T.bgElev2, borderRadius: 4, position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${level}%`, background: T.teal, borderRadius: 4 }} />
        <div style={{ position: "absolute", left: `${target}%`, top: -2, bottom: -2, width: 2, background: T.tan }} />
      </div>
    </div>
  );
}
