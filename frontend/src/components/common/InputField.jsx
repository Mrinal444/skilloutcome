import React, { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { T } from "../../theme.js";

export default function InputField({ icon: Icon, type = "text", placeholder, value, onChange }) {
  const [show, setShow] = useState(false);
  const isPw = type === "password";
  return (
    <div style={{ position: "relative", marginBottom: 14 }}>
      <Icon size={16} color={T.textFaint} style={{ position: "absolute", left: 14, top: 14 }} />
      <input
        className="sk-input"
        type={isPw && show ? "text" : type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        style={isPw ? { paddingRight: 40 } : undefined}
      />
      {isPw && (
        <button
          onClick={() => setShow((s) => !s)}
          aria-label="Toggle password visibility"
          style={{ position: "absolute", right: 12, top: 11, background: "none", border: "none", cursor: "pointer" }}
        >
          {show ? <EyeOff size={16} color={T.textFaint} /> : <Eye size={16} color={T.textFaint} />}
        </button>
      )}
    </div>
  );
}
