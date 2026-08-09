import React, { useEffect, useState } from "react";
import { getScenarios, simulate, getGraph } from "./api/client";
import ScenarioPicker from "./components/ScenarioPicker";
import Metrics from "./components/Metrics";
import AttackPath from "./components/AttackPath";
import MitreAndActions from "./components/MitreAndActions";
import GraphVisualization from "./components/GraphVisualization";
import AskBob from "./components/AskBob";
import Counterfactual from "./components/Counterfactual";
import "./App.css";

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [selected, setSelected] = useState("SC004");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState(null);
  const [graphData, setGraphData] = useState(null);

  useEffect(() => {
    getScenarios()
      .then((d) => setScenarios(d.scenarios))
      .catch((e) => setError(e.message));

    getGraph()
      .then((g) => setGraphData(g))
      .catch(() => {});

    // Run default scenario SC004 Developer takeover on startup
    run("SC004");
  }, []);

  async function run(scenarioId) {
    setSelected(scenarioId);
    setResult(null);
    setError(null);

    setStatus("Mapping accessible systems...");

    try {
      const data = await simulate(scenarioId);
      setStatus("");
      setResult(data);
    } catch (e) {
      setStatus("");
      setError(e.message);
    }
  }

  return (
    <div className="page">
      {/* 1. Header Bar matching photo */}
      <div className="header-bar">
        <div className="header-title">
          <span style={{ fontSize: 22 }}>🌀</span> BreachLens
        </div>
        <div className="header-badge">
          GET /graph &middot; 40 assets
        </div>
      </div>

      {error && <div className="card" style={{ borderColor: "#ef4444", color: "#dc2626" }}>Error: {error}</div>}

      {/* 2. Scenario Picker matching photo */}
      <ScenarioPicker
        scenarios={scenarios}
        selected={selected}
        onSelect={run}
        busy={status !== ""}
      />

      {status && (
        <div className="card muted" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span>⏳</span> {status}
        </div>
      )}

      {result && (
        <>
          {/* 3. Metric Cards matching photo */}
          <Metrics result={result} />

          {/* 4. Attack Path matching photo */}
          <AttackPath result={result} />

          {/* 5. 2-Column Split: MITRE techniques & Recommended actions matching photo */}
          <MitreAndActions result={result} />

          {/* 6. Interactive Network Graph (Bigger & Spaced) */}
          <GraphVisualization result={result} graphData={graphData} />

          {/* 7. Ask about this incident matching photo */}
          <AskBob incident={result} />

          {/* 8. What to fix first / Counterfactual Analysis */}
          <Counterfactual scenarioId={selected} />
        </>
      )}
    </div>
  );
}
