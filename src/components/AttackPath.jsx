import React, { useEffect, useState } from "react";

export default function AttackPath({ result }) {
  const path = result.headline_path;
  const [shown, setShown] = useState(0);

  // Friendly display names for path nodes matching photo
  const friendlyNames = {
    jira: "Jira",
    github_org: "GitHub org",
    repo_payments: "payments-api",
    aws_prod_account: "AWS prod",
    s3_customer_backups: "S3 backups",
    prod_db_master: "Customer DB",
    zendesk: "Zendesk",
    salesforce: "Salesforce"
  };

  useEffect(() => {
    if (!path) return;
    setShown(0);
    const timer = setInterval(() => {
      setShown((n) => {
        if (n >= path.path.length) {
          clearInterval(timer);
          return n;
        }
        return n + 1;
      });
    }, 500);
    return () => clearInterval(timer);
  }, [result?.start_asset, path]);

  if (!path) {
    return (
      <div className="attack-path-box">
        <div className="card-title">Attack path</div>
        <div className="card-subtitle">No path to a data store in this scenario.</div>
      </div>
    );
  }

  const pathList = path.path;
  const activeStep = path.steps && path.steps.length > 0 ? path.steps[Math.min(2, path.steps.length - 1)] : null;

  return (
    <div className="attack-path-box">
      <div className="card-title">Attack path</div>
      <div className="card-subtitle">Discovered by traversal, not authored</div>

      <div className="chain-container">
        {pathList.map((id, i) => {
          const isTarget = i === pathList.length - 1;
          const name = friendlyNames[id] || id;

          return (
            <React.Fragment key={id}>
              <div
                className={`chain-pill ${i < shown ? "show" : ""} ${isTarget ? "target" : ""}`}
              >
                {name}
              </div>
              {i < pathList.length - 1 && (
                <span className="chain-arrow">&rarr;</span>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {activeStep && (
        <div className="step-summary">
          <span style={{ color: "var(--muted)", marginRight: 6 }}>Step {activeStep.step}</span>
          <span className="step-tag">{activeStep.mitre_technique}</span>
          {activeStep.reason}
        </div>
      )}
    </div>
  );
}
