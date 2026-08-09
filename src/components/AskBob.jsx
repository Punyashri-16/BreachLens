import React, { useState } from "react";
import { askBob } from "../api/client";

export default function AskBob({ incident }) {
  const defaultQuestion = "Why is the customer database compromised?";
  const defaultAnswer = "It is reachable in five steps. Jira shares single sign-on with the GitHub organisation, which grants read access to the payments-api repository. That repository contains a hardcoded AWS deploy key, and the customer database backups live in that same AWS account.";

  const [question, setQuestion] = useState(defaultQuestion);
  const [answer, setAnswer] = useState(defaultAnswer);
  const [busy, setBusy] = useState(false);

  async function handleAsk() {
    if (!question) return;
    setBusy(true);
    try {
      const result = await askBob(question, incident);
      setAnswer(result.answer);
    } catch (e) {
      setAnswer("Could not answer: " + e.message);
    }
    setBusy(false);
  }

  return (
    <div className="ask-box">
      <div className="card-title" style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 12 }}>
        <span>💬</span> Ask about this incident
      </div>

      <div style={{ position: "relative" }}>
        <input
          className="ask-input"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask a question about this scenario..."
        />
      </div>

      {answer && (
        <div className="answer-card">
          {answer}
          <div style={{ textAlign: "center", marginTop: 8 }}>
            <span style={{ fontSize: 12, color: "var(--muted)", cursor: "pointer" }}>↓</span>
          </div>
        </div>
      )}
    </div>
  );
}
