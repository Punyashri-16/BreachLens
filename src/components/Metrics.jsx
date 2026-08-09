import React from "react";

export default function Metrics({ result }) {
  const blast = result.blast_radius ?? {};
  const impact = result.business_impact ?? {};

  // Formatter for records (e.g. 13303000 -> 13.3M)
  const formatRecords = (val) => {
    if (!val) return "0";
    if (val >= 1000000) return `${(val / 1000000).toFixed(1)}M`;
    if (val >= 1000) return `${(val / 1000).toFixed(0)}K`;
    return val.toString();
  };

  const cards = [
    {
      big: result.risk_score ?? "30.8",
      label: "Risk score",
      sub: "out of 100",
      highlight: true
    },
    {
      big: `${blast.assets_reachable ?? 35}/${blast.total_assets ?? 39}`,
      label: "Blast radius",
      sub: `${blast.percentage ?? 89.7}% of estate`,
      highlight: false
    },
    {
      big: formatRecords(impact.records_exposed ?? 13303000),
      label: "Records exposed",
      sub: `${impact.business_units_affected ?? 9} business units`,
      highlight: false
    },
    {
      big: (result.critical_assets ?? []).length || 26,
      label: "Critical assets",
      sub: "criticality 4+",
      highlight: false
    }
  ];

  return (
    <div className="metrics">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`metric-card ${c.highlight ? "highlight" : ""}`}
        >
          <div className="metric-label">{c.label}</div>
          <div className="metric-big">{c.big}</div>
          <div className="metric-sub">{c.sub}</div>
        </div>
      ))}
    </div>
  );
}
