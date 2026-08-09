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

    // A short delay with status messages. An instant result feels
    // cheap, and two seconds of tension makes the demo land.
    setStatus("Employee clicked the link...");
    setTimeout(() => setStatus("Mapping accessible systems..."), 700);
    setTimeout(() => setStatus("Calculating blast radius..."), 1400);

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
      <h1>BreachLens</h1>
      <p className="muted">
        If one system is compromised, how far can the attacker get?
      </p>

      {error && <div className="card">Error: {error}</div>}

      <ScenarioPicker
        scenarios={scenarios}
        selected={selected}
        onSelect={run}
        busy={status !== ""}
      />

      {status && <div className="card muted">{status}</div>}

      {result && (
        <>
          <h2>{result.scenario?.name}</h2>
          <Metrics result={result} />
          <h2>How the attacker moves</h2>
          <AttackPath result={result} />
          <h2>Network topology & attack path graph</h2>
          <GraphVisualization result={result} graphData={graphData} />
          <h2>Recommended action</h2>
          <Counterfactual scenarioId={selected} />
          <h2>Questions</h2>
          <AskBob incident={result} />
        </>
      )}
    </div>
  );
}
