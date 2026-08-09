import { useEffect, useState } from "react";
import { getCounterfactual } from "../api/client";

export default function Counterfactual({ scenarioId }) {
  const [data, setData] = useState(null);
  const [picked, setPicked] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setData(null);
    setPicked(null);
    setError(null);
    getCounterfactual(scenarioId, 5)
      .then(setData)
      .catch((e) => setError(e.message));
  }, [scenarioId]);

  if (error) return <div className="card">Could not load: {error}</div>;
  if (!data) return <div className="card muted">Testing every connection...</div>;

  const shownScore = picked ? picked.new_score : data.baseline_score;

  return (
    <div className="card">
      <div style={{ fontSize: 14, marginBottom: 4 }}>What to fix first</div>
      <div className="muted" style={{ fontSize: 12, marginBottom: 14 }}>
        We removed each connection, re-ran the analysis, and ranked by improvement.
        {" "}{data.edges_tested} connections tested.
      </div>

      <div style={{ fontSize: 34, fontWeight: 600, marginBottom: 14 }}>
        {shownScore}
        <span className="muted" style={{ fontSize: 16 }}> / 100</span>
        {picked && (
          <span className="drop" style={{ fontSize: 16, marginLeft: 10 }}>
            −{picked.percent_drop}%
          </span>
        )}
      </div>

      {data.recommendations.map((r) => (
        <div
          key={`${r.source}-${r.target}`}
          className={`card fix ${picked === r ? "active" : ""}`}
          onClick={() => setPicked(picked === r ? null : r)}
        >
          <div style={{ fontSize: 13 }}>
            Cut <strong>{r.source_name}</strong> &rarr; <strong>{r.target_name}</strong>
          </div>
          <div style={{ fontSize: 12, margin: "4px 0" }}>
            {r.baseline_score} &rarr; {r.new_score}{" "}
            <span className="drop">−{r.percent_drop}%</span>
          </div>
          <div className="muted" style={{ fontSize: 11 }}>
            {r.reason}
          </div>
          <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>
            {r.assets_closed > 0
              ? `Closes off ${r.assets_closed} systems`
              : "Closes nothing — makes everything harder to reach"}
          </div>
        </div>
      ))}
    </div>
  );
}
