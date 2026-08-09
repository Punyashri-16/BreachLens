import React from "react";

export default function ScenarioPicker({ scenarios, selected, onSelect, busy }) {
  const displayScenarios = scenarios.slice(0, 3);
  const remainingCount = Math.max(0, scenarios.length - 3);

  return (
    <div className="scenario-box">
      <div className="scenario-header">
        Choose a scenario <code>GET /scenarios</code>
      </div>
      <div className="scenario-pills">
        {displayScenarios.map((s) => (
          <button
            key={s.id}
            className={`scenario-btn ${selected === s.id ? "active" : ""}`}
            disabled={busy}
            onClick={() => onSelect(s.id)}
          >
            {s.id} {s.name}
          </button>
        ))}
        {scenarios.map((s) => {
          if (displayScenarios.find((ds) => ds.id === s.id)) return null;
          return (
            <button
              key={s.id}
              className={`scenario-btn ${selected === s.id ? "active" : ""}`}
              disabled={busy}
              onClick={() => onSelect(s.id)}
            >
              {s.id} {s.name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
