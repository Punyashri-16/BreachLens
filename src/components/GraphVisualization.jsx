import React, { useRef, useEffect, useState } from "react";
import { MOCK_NODES, MOCK_EDGES } from "../data/mockGraphData";

// Zone layout positioning for 40 nodes in cybersecurity network tiers
const TIER_Y = {
  perimeter: 50,
  endpoint: 120,
  saas: 190,
  iam: 190,
  scm: 260,
  code: 260,
  devops: 260,
  compute: 340,
  cloud: 340,
  database: 420,
  storage: 420,
  secret: 340,
  monitoring: 420
};

export default function GraphVisualization({ result, graphData }) {
  const canvasRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [viewMode, setViewMode] = useState("all"); // "all" | "attack_path"
  const [zoom, setZoom] = useState(1);

  const nodes = graphData?.nodes || MOCK_NODES;
  const edges = graphData?.edges || MOCK_EDGES;

  // Active path IDs from scenario simulation result
  const activePathIds = result?.headline_path?.path || [];
  const activeStepEdges = result?.headline_path?.steps || [];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    
    // Set up responsive DPI high quality rendering
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Compute positions for 40 nodes in grid layout across 6 horizontal bands
    const width = rect.width;
    const height = rect.height;

    // Group nodes by tier to compute X positions evenly
    const tierGroups = {};
    nodes.forEach(n => {
      const tier = TIER_Y[n.type] ? n.type : "compute";
      if (!tierGroups[tier]) tierGroups[tier] = [];
      tierGroups[tier].push(n);
    });

    const nodePos = {};
    Object.keys(tierGroups).forEach(tier => {
      const group = tierGroups[tier];
      const y = (TIER_Y[tier] / 480) * height;
      group.forEach((node, i) => {
        const spacing = width / (group.length + 1);
        nodePos[node.id] = {
          x: spacing * (i + 1),
          y: y,
          node
        };
      });
    });

    let animationFrameId;
    let particleOffset = 0;

    const render = () => {
      particleOffset = (particleOffset + 0.8) % 100;
      ctx.clearRect(0, 0, width, height);

      // Draw background grid lines
      ctx.strokeStyle = "rgba(44, 48, 56, 0.4)";
      ctx.lineWidth = 1;
      for (let x = 0; x < width; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw 58 directed edges
      edges.forEach(edge => {
        const src = nodePos[edge.source];
        const tgt = nodePos[edge.target];
        if (!src || !tgt) return;

        const isPathEdge = activePathIds.includes(edge.source) && activePathIds.includes(edge.target) &&
          activePathIds.indexOf(edge.target) === activePathIds.indexOf(edge.source) + 1;

        if (viewMode === "attack_path" && !isPathEdge) return;

        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);

        if (isPathEdge) {
          ctx.strokeStyle = "#ef4444";
          ctx.lineWidth = 3;
          ctx.setLineDash([6, 4]);
          ctx.lineDashOffset = -particleOffset;
        } else {
          ctx.strokeStyle = "rgba(100, 116, 139, 0.25)";
          ctx.lineWidth = 1;
          ctx.setLineDash([]);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // Draw arrow heads on active path edges
        if (isPathEdge) {
          const angle = Math.atan2(tgt.y - src.y, tgt.x - src.x);
          const arrowLen = 8;
          ctx.fillStyle = "#ef4444";
          ctx.beginPath();
          ctx.moveTo(tgt.x - 12 * Math.cos(angle), tgt.y - 12 * Math.sin(angle));
          ctx.lineTo(
            tgt.x - 12 * Math.cos(angle) - arrowLen * Math.cos(angle - Math.PI / 6),
            tgt.y - 12 * Math.sin(angle) - arrowLen * Math.sin(angle - Math.PI / 6)
          );
          ctx.lineTo(
            tgt.x - 12 * Math.cos(angle) - arrowLen * Math.cos(angle + Math.PI / 6),
            tgt.y - 12 * Math.sin(angle) - arrowLen * Math.sin(angle + Math.PI / 6)
          );
          ctx.fill();
        }
      });

      // Draw 40 nodes
      nodes.forEach(n => {
        const pos = nodePos[n.id];
        if (!pos) return;

        const isActivePath = activePathIds.includes(n.id);
        const isStartNode = activePathIds[0] === n.id;
        const isTargetNode = activePathIds[activePathIds.length - 1] === n.id;

        if (viewMode === "attack_path" && !isActivePath) return;

        // Outer halo glow for active attack path nodes
        if (isActivePath) {
          ctx.beginPath();
          ctx.arc(pos.x, pos.y, 14, 0, Math.PI * 2);
          ctx.fillStyle = isStartNode || isTargetNode ? "rgba(239, 68, 68, 0.35)" : "rgba(249, 115, 22, 0.25)";
          ctx.fill();
        }

        // Inner node circle
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 7, 0, Math.PI * 2);

        if (isStartNode) {
          ctx.fillStyle = "#ef4444"; // Entry point bright red
        } else if (isTargetNode) {
          ctx.fillStyle = "#dc2626"; // Compromised target dark red
        } else if (isActivePath) {
          ctx.fillStyle = "#f97316"; // Hop orange
        } else if (n.criticality >= 4) {
          ctx.fillStyle = "#3b82f6"; // Critical asset blue
        } else {
          ctx.fillStyle = "#64748b"; // Standard node slate
        }

        ctx.fill();
        ctx.strokeStyle = "#1e2126";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Label node name
        ctx.fillStyle = isActivePath ? "#ffffff" : "#9aa0a6";
        ctx.font = isActivePath ? "bold 11px system-ui" : "10px system-ui";
        ctx.textAlign = "center";
        ctx.fillText(n.name || n.id, pos.x, pos.y + 18);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    // Mouse interactive hover detection
    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let found = null;
      Object.values(nodePos).forEach(pos => {
        const dx = mx - pos.x;
        const dy = my - pos.y;
        if (dx * dx + dy * dy <= 100) {
          found = pos.node;
        }
      });
      setHoveredNode(found);
    };

    canvas.addEventListener("mousemove", handleMouseMove);

    return () => {
      cancelAnimationFrame(animationFrameId);
      canvas.removeEventListener("mousemove", handleMouseMove);
    };
  }, [nodes, edges, activePathIds, viewMode]);

  return (
    <div className="card">
      <div className="graph-header">
        <div>
          <div style={{ fontSize: 14, fontWeight: 600 }}>Network Topology & Attack Graph</div>
          <div className="muted" style={{ fontSize: 12 }}>
            Interactive visualization of {nodes.length} assets & {edges.length} connections
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            style={{ fontSize: 12, padding: "4px 10px" }}
            className={viewMode === "all" ? "active" : ""}
            onClick={() => setViewMode("all")}
          >
            All 40 Nodes
          </button>
          <button
            style={{ fontSize: 12, padding: "4px 10px" }}
            className={viewMode === "attack_path" ? "active" : ""}
            onClick={() => setViewMode("attack_path")}
          >
            Attack Path Only
          </button>
        </div>
      </div>

      <div className="graph-canvas-container">
        <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
      </div>

      {hoveredNode && (
        <div style={{
          marginTop: 10,
          padding: "8px 12px",
          background: "#1e2126",
          border: "1px solid #3b82f6",
          borderRadius: 6,
          fontSize: 12,
          display: "flex",
          justify-content: "space-between",
          alignItems: "center"
        }}>
          <div>
            <strong>{hoveredNode.name}</strong> ({hoveredNode.id}) — <span className="muted">{hoveredNode.unit}</span>
          </div>
          <div>
            Criticality: <span style={{ color: hoveredNode.criticality >= 4 ? "#ef4444" : "#3b82f6" }}>{hoveredNode.criticality}/5</span>
            {hoveredNode.record_count > 0 && ` | Records: ${hoveredNode.record_count.toLocaleString()}`}
          </div>
        </div>
      )}

      <div className="graph-legend">
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#ef4444" }}></div>
          <span>Start Asset (Entrypoint)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#f97316" }}></div>
          <span>Traversal Hop</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#dc2626" }}></div>
          <span>Compromised Target</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#3b82f6" }}></div>
          <span>Critical Asset (&ge;4)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#64748b" }}></div>
          <span>Infrastructure Node</span>
        </div>
      </div>
    </div>
  );
}
