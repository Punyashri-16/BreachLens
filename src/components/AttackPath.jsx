import { useEffect, useState } from "react";

export default function AttackPath({ result }) {
  const path = result.headline_path;
  const [shown, setShown] = useState(0);

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
    }, 600);
    return () => clearInterval(timer);
  }, [result.start_asset, path]);

  if (!path) {
    return (
      <div className="card">
        <div className="muted">No path to a data store in this scenario.</div>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ fontSize: 14, marginBottom: 4 }}>Attack path</div>
      <div className="muted" style={{ fontSize: 12, marginBottom: 14 }}>
        Discovered by traversal, not written by us
      </div>

      <div className="chain">
        {path.path.map((id, i) => (
          <span key={id} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span className={`node ${i < shown ? "show" : ""} ${i === 0 || i === path.path.length - 1 ? "hot" : ""}`}>
              {id}
            </span>
            {i < path.path.length - 1 && <span className="muted">&rarr;</span>}
          </span>
        ))}
      </div>

      {shown >= path.path.length && (
        <div style={{ marginTop: 14, paddingTop: 12, borderTop: "1px solid var(--line)" }}>
          {path.steps.map((s) => (
            <div key={s.step} style={{ fontSize: 12, marginBottom: 6 }}>
              <span className="muted">Step {s.step}</span>{" "}
              <span style={{ color: "#ffb4b4" }}>{s.mitre_technique}</span>{" "}
              {s.reason}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
