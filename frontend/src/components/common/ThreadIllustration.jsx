import React from "react";
import { T } from "../../theme.js";

const STAGES = ["Enrolled", "Trained", "Assessed", "Placed"];
const POINTS = [
  { x: 40, y: 40 },
  { x: 160, y: 150 },
  { x: 160, y: 260 },
  { x: 160, y: 380 },
];

export default function ThreadIllustration() {
  return (
    <svg viewBox="0 0 320 420" width="100%" height="100%" style={{ maxWidth: 300 }}>
      <path
        d="M40 40 C 160 40, 40 150, 160 150 S 280 260, 160 260 S 40 370, 160 380"
        fill="none"
        stroke={T.tealDeep}
        strokeWidth="2"
      />
      <path
        d="M40 40 C 160 40, 40 150, 160 150 S 280 260, 160 260 S 40 370, 160 380"
        fill="none"
        stroke={T.teal}
        strokeWidth="2"
        className="sk-thread"
        opacity="0.8"
      />
      {POINTS.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r="6" fill={T.bg} stroke={T.teal} strokeWidth="2" />
          <text x={p.x + 16} y={p.y + 4} fill={T.textDim} fontSize="12" fontFamily="Inter">
            {STAGES[i]}
          </text>
        </g>
      ))}
    </svg>
  );
}
