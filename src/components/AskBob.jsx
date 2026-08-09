import { useState } from "react";
import { askBob } from "../api/client";

export default function AskBob({ incident }) {
  const [question, setQuestion] = useState("Why is the customer database compromised?");
  const [answer, setAnswer] = useState(null);
  const [busy, setBusy] = useState(false);

  async function ask() {
    setBusy(true);
    setAnswer(null);
    try {
      const result = await askBob(question, incident);
      setAnswer(result.answer);
    } catch (e) {
      setAnswer("Could not answer: " + e.message);
    }
    setBusy(false);
  }

  return (
    <div className="card">
      <div style={{ fontSize: 14, marginBottom: 10 }}>Ask about this incident</div>
      <input
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{
          width: "100%", padding: "9px 12px", fontSize: 13,
          background: "transparent", color: "var(--text)",
          border: "1px solid var(--line)", borderRadius: 6, marginBottom: 10,
        }}
      />
      <button onClick={ask} disabled={busy}>
        {busy ? "Thinking..." : "Ask"}
      </button>
      {answer && (
        <div style={{
          marginTop: 12, paddingLeft: 12, fontSize: 13,
          lineHeight: 1.6, borderLeft: "2px solid var(--line)",
        }}>
          {answer}
        </div>
      )}
    </div>
  );
}
