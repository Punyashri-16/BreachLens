export default function Metrics({ result }) {
  const blast = result.blast_radius ?? {};
  const impact = result.business_impact ?? {};

  const cards = [
    {
      big: result.risk_score ?? "—",
      label: "Risk score",
      note: "out of 100",
    },
    {
      big: `${blast.assets_reachable ?? 0}/${blast.total_assets ?? 0}`,
      label: "Blast radius",
      note: `${blast.percentage ?? 0}% of the estate`,
    },
    {
      big: (impact.records_exposed ?? 0).toLocaleString(),
      label: "Records exposed",
      note: `${impact.business_units_affected ?? 0} business units`,
    },
    {
      big: (result.critical_assets ?? []).length,
      label: "Critical assets",
      note: "criticality 4 and above",
    },
  ];

  return (
    <div className="metrics">
      {cards.map((c) => (
        <div className="card metric" key={c.label}>
          <div className="big">{c.big}</div>
          <div>{c.label}</div>
          <small>{c.note}</small>
        </div>
      ))}
    </div>
  );
}
