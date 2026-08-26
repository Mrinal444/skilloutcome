import React from "react";
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";
import { T } from "../../theme.js";

export default function ProgressRing({ value, size = 96 }) {
  const data = [{ value, fill: T.teal }];
  return (
    <div style={{ width: size, height: size, position: "relative" }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadialBarChart innerRadius="72%" outerRadius="100%" data={data} startAngle={90} endAngle={-270}>
          <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
          <RadialBar background={{ fill: T.bgElev2 }} dataKey="value" cornerRadius={20} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column",
        }}
      >
        <span className="sk-mono" style={{ fontSize: 18, fontWeight: 500 }}>
          {value}%
        </span>
      </div>
    </div>
  );
}
