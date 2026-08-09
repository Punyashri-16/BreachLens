import { useEffect, useState } from "react";
import { getScenarios, simulate, getGraph } from "./api/client";
import ScenarioPicker from "./components/ScenarioPicker";
import Metrics from "./components/Metrics";
import AttackPath from "./components/AttackPath";
import Counterfactual from "./components/Counterfactual";
import AskBob from "./components/AskBob";
import GraphVisualization from "./components/GraphVisualization";
import "./App.css";

export default function App() {
  const [scenarios, setScenarios] = useState([]);
  const [selected, setSelected] = useState(null);
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
  }, []);

  async function run(scenarioId) {
    setSelected(scenarioId);
    setResult(null);
    setError(null);

    // Progressive status updates for realistic analysis feedback
    setStatus("Employee clicked the link...");
    setTimeout(() => setStatus("Mapping accessible systems across 40 nodes..."), 700);
    setTimeout(() => setStatus("Calculating blast radius & record exposure..."), 1400);

    try {
      const data = await simulate(scenarioId);
      setTimeout(() => {
        setStatus("");
        setResult(data);
      }, 2100);
    } catch (e) {
      setStatus("");
      setError(e.message);
    }
  }

  return (
    <div className="page">
      <div className="header-brand">
        <span style={{ fontSize: 28 }}>🛡️</span>
        <h1>BreachLens</h1>
      </div>
      <p className="muted" style={{ margin: "0 0 24px 0", fontSize: 14 }}>
        Automated Security Graph Traversal — If one system is compromised, how far can the attacker get?
      </p>

      {error && <div className="card" style={{ borderColor: "#ef4444" }}>Error: {error}</div>}

      <ScenarioPicker
        scenarios={scenarios}
        selected={selected}
        onSelect={run}
        busy={status !== ""}
      />

      {status && (
        <div className="card muted" style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ animation: "spin 1s infinite linear" }}>⏳</span>
          {status}
        </div>
      )}

      {result && (
        <>
          <h2>📊 {result.scenario?.name}</h2>
          <Metrics result={result} />

          <h2>🔍 How the Attacker Moves</h2>
          <AttackPath result={result} />

          <h2>🌐 Network Topology & Attack Traversal Graph</h2>
          <GraphVisualization result={result} graphData={graphData} />

          <h2>🛠️ Recommended Action ("What to Fix First")</h2>
          <Counterfactual scenarioId={selected} />

          <h2>💬 Ask Bob & Business Impact</h2>
          <AskBob incident={result} />
        </>
      )}
    </div>
  );
}
