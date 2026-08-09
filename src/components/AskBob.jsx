import { useState } from "react";
import { askBob } from "../api/client";

export default function AskBob({ incident }) {
  const [question, setQuestion] = useState("Explain this attack in simple terms like I'm 5");
  const [answer, setAnswer] = useState(null);
  const [busy, setBusy] = useState(false);

  const suggestedQuestions = [
    "Explain this attack in simple terms like I'm 5",
    "What is the financial & business risk?",
    "What single fix stops this attack immediately?",
    "Why was the database reached so easily?"
  ];

  async function handleAsk(qToAsk) {
    const query = qToAsk || question;
    setBusy(true);
    setAnswer(null);
    try {
      const result = await askBob(query, incident);
      setAnswer(result.answer);
    } catch (e) {
      setAnswer("Could not answer: " + e.message);
    }
    setBusy(false);
  }

  const recordsExposed = (incident?.business_impact?.records_exposed || 13303000).toLocaleString();
  const startAssetName = incident?.start_asset_name || "Jira";
  const reachableCount = incident?.blast_radius?.assets_reachable || 35;

  return (
    <div>
      {/* 1. Dedicated Business Impact Section in Simple Terms */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 15, fontWeight: 600, color: "#f8fafc", marginBottom: 4 }}>
          💼 Business Impact Summary (Executive View)
        </div>
        <div className="muted" style={{ fontSize: 12.5, marginBottom: 14 }}>
          How this security breach directly affects revenue, compliance, and daily operations
        </div>

        <div className="business-impact-grid">
          <div className="impact-card">
            <div className="impact-icon">💰</div>
            <div className="impact-title">Financial & Compliance Fines</div>
            <div className="impact-desc">
              Exposing <strong>{recordsExposed} records</strong> triggers mandatory breach notifications under GDPR and CCPA. Fines can reach up to 4% of global turnover or $20M+ in legal payouts.
            </div>
          </div>

          <div className="impact-card">
            <div className="impact-icon">🛑</div>
            <div className="impact-title">Operational Downtime</div>
            <div className="impact-desc">
              With <strong>{reachableCount} systems compromised</strong>, security operations will be forced to isolate the AWS cloud environment, freezing developer code updates and billing services.
            </div>
          </div>

          <div className="impact-card">
            <div className="impact-icon">🛡️</div>
            <div className="impact-title">Reputational & Brand Damage</div>
            <div className="impact-desc">
              A breach starting at <strong>{startAssetName}</strong> and reaching production databases undermines enterprise customer trust, risking contract cancellations and brand devaluation.
            </div>
          </div>
        </div>
      </div>

      {/* 2. Interactive Plain-English AI Incident Assistant */}
      <div className="card">
        <div style={{ fontSize: 15, fontWeight: 600, color: "#f8fafc", marginBottom: 4 }}>
          🤖 Ask Bob — AI Incident Assistant
        </div>
        <div className="muted" style={{ fontSize: 12.5, marginBottom: 12 }}>
          Ask any question in plain English to understand how the attacker moved and how to protect the business
        </div>

        {/* Quick Suggestion Pills */}
        <div className="question-pills">
          {suggestedQuestions.map((sq) => (
            <button
              key={sq}
              className="pill-btn"
              onClick={() => {
                setQuestion(sq);
                handleAsk(sq);
              }}
            >
              💡 {sq}
            </button>
          ))}
        </div>

        <div className="ask-input-group">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            placeholder="Type your question in plain English..."
            style={{
              width: "100%",
              padding: "10px 14px",
              fontSize: 13.5,
              background: "#080c14",
              color: "var(--text)",
              border: "1px solid #1e293b",
              borderRadius: 8,
              outline: "none"
            }}
          />
          <button
            onClick={() => handleAsk()}
            disabled={busy}
            style={{ width: "fit-content" }}
          >
            {busy ? "Analyzing Graph..." : "Ask AI"}
          </button>
        </div>

        {answer && (
          <div className="ai-answer-box">
            <div className="ai-badge">
              ⚡ AI Plain-English Explanation
            </div>
            <div style={{ color: "#f1f5f9", lineHeight: "1.6" }}>
              {answer}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
