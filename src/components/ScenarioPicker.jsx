export default function ScenarioPicker({ scenarios, selected, onSelect, busy }) {
  return (
    <div className="card">
      <div className="muted" style={{ fontSize: 13, marginBottom: 10 }}>
        Choose an attack scenario
      </div>
      {scenarios.map((s) => (
        <button
          key={s.id}
          className={selected === s.id ? "active" : ""}
          disabled={busy}
          onClick={() => onSelect(s.id)}
        >
          {s.id} — {s.name}
        </button>
      ))}
    </div>
  );
}
