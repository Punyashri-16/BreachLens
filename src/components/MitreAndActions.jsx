import React from "react";

export default function MitreAndActions({ result }) {
  const mitre = result?.mitre ?? {};
  const techniques = mitre.techniques ?? [
    { technique_id: "T1078", name: "Valid accounts", occurrences: 14 },
    { technique_id: "T1552", name: "Unsecured creds", occurrences: 6 },
    { technique_id: "T1530", name: "Cloud storage", occurrences: 5 }
  ];

  const actions = [
    "Rotate the deploy key in payments-api",
    "Break repo access from GitHub org",
    "Scope the CI production role"
  ];

  return (
    <div className="split-grid">
      {/* Left Box: MITRE techniques */}
      <div className="split-box">
        <div className="card-title">MITRE techniques</div>
        <div className="mitre-list">
          {techniques.slice(0, 3).map((t) => (
            <div key={t.technique_id} className="mitre-row">
              <span className="mitre-code">{t.technique_id}</span>
              <span className="mitre-name">{t.name}</span>
              <span className="mitre-count">&times;{t.occurrences}</span>
            </div>
          ))}
          <div className="card-subtitle" style={{ marginTop: 8, marginBottom: 0 }}>
            +6 more across 5 tactics
          </div>
        </div>
      </div>

      {/* Right Box: Recommended actions */}
      <div className="split-box">
        <div className="card-title">Recommended actions</div>
        <div className="actions-list">
          {actions.map((action, idx) => (
            <div key={idx} className="action-item">
              <span className="action-num">{idx + 1}</span>
              <span>{action}</span>
            </div>
          ))}
          <div className="card-subtitle" style={{ marginTop: 4, marginBottom: 0 }}>
            +3 more
          </div>
        </div>
      </div>
    </div>
  );
}
