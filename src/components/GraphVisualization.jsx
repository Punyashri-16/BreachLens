import React, { useRef, useEffect, useState } from "react";
import { MOCK_NODES, MOCK_EDGES } from "../data/mockGraphData";

const TIER_Y = {
  perimeter: 0.10,
  endpoint: 0.12,
  saas: 0.28,
  iam: 0.30,
  scm: 0.48,
  code: 0.50,
  devops: 0.52,
  compute: 0.70,
  cloud: 0.72,
  secret: 0.74,
  database: 0.88,
  storage: 0.90,
  monitoring: 0.92
};

export default function GraphVisualization({ result, graphData }) {
  const canvasRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [viewMode, setViewMode] = useState("all");
  const [zoom, setZoom] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");

  const nodes = graphData?.nodes || MOCK_NODES;
  const edges = graphData?.edges || MOCK_EDGES;

  const activePathIds = result?.headline_path?.path || [];

  // Filter nodes based on search query
  const filteredNodes = nodes.filter(n => 
    n.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    n.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    const rect = canvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Compute positions with wide spacing to avoid word overlap
    const nodePos = {};
    const groups = {};

    nodes.forEach(n => {
      const tier = n.type || "compute";
      if (!groups[tier]) groups[tier] = [];
      groups[tier].push(n);
    });

    Object.keys(groups).forEach(tier => {
      const tierNodes = groups[tier];
      const yRatio = TIER_Y[tier] || 0.5;
      const baseY = yRatio * height;

      tierNodes.forEach((node, idx) => {
        const spacing = (width - 140) / (tierNodes.length + 1);
        const staggerY = (idx % 2 === 0 ? -22 : 22);
        nodePos[node.id] = {
          x: 70 + spacing * (idx + 1),
          y: Math.max(45, Math.min(height - 45, baseY + staggerY)),
          labelPos: idx % 2 === 0 ? "top" : "bottom",
          node
        };
      });
    });

    let animFrame;
    let animTime = 0;

    const render = () => {
      animTime += 0.04;
      ctx.clearRect(0, 0, width, height);

      // Light grid background
      ctx.strokeStyle = "rgba(226, 232, 240, 0.6)";
      ctx.lineWidth = 1;
      for (let x = 0; x < width; x += 60) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += 60) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw Edges (58 connections)
      edges.forEach(edge => {
        const src = nodePos[edge.source];
        const tgt = nodePos[edge.target];
        if (!src || !tgt) return;

        const isPathEdge = activePathIds.includes(edge.source) &&
          activePathIds.includes(edge.target) &&
          activePathIds.indexOf(edge.target) === activePathIds.indexOf(edge.source) + 1;

        if (viewMode === "attack_path" && !isPathEdge) return;

        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);

        if (isPathEdge) {
          ctx.strokeStyle = "#dc2626";
          ctx.lineWidth = 3;
          ctx.setLineDash([8, 4]);
          ctx.lineDashOffset = -animTime * 14;
        } else {
          ctx.strokeStyle = "rgba(148, 163, 184, 0.4)";
          ctx.lineWidth = 1.2;
          ctx.setLineDash([]);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // Animated flow particles along active attack path
        if (isPathEdge) {
          const progress = (animTime * 0.35) % 1;
          const px = src.x + (tgt.x - src.x) * progress;
          const py = src.y + (tgt.y - src.y) * progress;

          ctx.beginPath();
          ctx.arc(px, py, 5, 0, Math.PI * 2);
          ctx.fillStyle = "#ef4444";
          ctx.fill();
        }
      });

      // Draw 40 Nodes with high-contrast text pills
      nodes.forEach(n => {
        const pos = nodePos[n.id];
        if (!pos) return;

        const isActivePath = activePathIds.includes(n.id);
        const isStartNode = activePathIds[0] === n.id;
        const isTargetNode = activePathIds[activePathIds.length - 1] === n.id;
        const isHighlightedBySearch = searchQuery && (n.name.toLowerCase().includes(searchQuery.toLowerCase()) || n.id.toLowerCase().includes(searchQuery.toLowerCase()));

        if (viewMode === "attack_path" && !isActivePath) return;

        // Halo ring for active path nodes
        if (isActivePath) {
          const haloR = 15 + Math.sin(animTime * 3) * 3;
          ctx.beginPath();
          ctx.arc(pos.x, pos.y, haloR, 0, Math.PI * 2);
          ctx.fillStyle = isStartNode || isTargetNode ? "rgba(239, 68, 68, 0.25)" : "rgba(249, 115, 22, 0.2)";
          ctx.fill();
        }

        // Inner node dot
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 8, 0, Math.PI * 2);

        if (isStartNode) {
          ctx.fillStyle = "#dc2626";
        } else if (isTargetNode) {
          ctx.fillStyle = "#b91c1c";
        } else if (isActivePath) {
          ctx.fillStyle = "#ea580c";
        } else if (isHighlightedBySearch) {
          ctx.fillStyle = "#2563eb";
        } else if (n.criticality >= 4) {
          ctx.fillStyle = "#0284c7";
        } else {
          ctx.fillStyle = "#64748b";
        }

        ctx.fill();
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Node Label with Crisp Background Pill (Zero Character Overlap)
        const labelText = n.name || n.id;
        ctx.font = isActivePath ? "bold 11.5px system-ui" : "11px system-ui";
        const textMetrics = ctx.measureText(labelText);
        const textW = textMetrics.width;

        const ly = pos.labelPos === "top" ? pos.y - 14 : pos.y + 24;

        // Background pill
        ctx.fillStyle = isActivePath ? "rgba(254, 226, 226, 0.95)" : "rgba(255, 255, 255, 0.95)";
        ctx.beginPath();
        ctx.roundRect(pos.x - textW / 2 - 6, ly - 11, textW + 12, 16, 4);
        ctx.fill();
        ctx.strokeStyle = isActivePath ? "#fca5a5" : "#cbd5e1";
        ctx.lineWidth = 1;
        ctx.stroke();

        // Label text
        ctx.fillStyle = isActivePath ? "#991b1b" : "#0f172a";
        ctx.textAlign = "center";
        ctx.fillText(labelText, pos.x, ly);
      });

      animFrame = requestAnimationFrame(render);
    };

    render();

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let found = null;
      Object.values(nodePos).forEach(pos => {
        const dx = mx - pos.x;
        const dy = my - pos.y;
        if (dx * dx + dy * dy <= 160) {
          found = pos.node;
        }
      });
      setHoveredNode(found);
    };

    canvas.addEventListener("mousemove", handleMouseMove);

    return () => {
      cancelAnimationFrame(animFrame);
      canvas.removeEventListener("mousemove", handleMouseMove);
    };
  }, [nodes, edges, activePathIds, viewMode, searchQuery]);

  return (
    <div className="graph-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14, flexWrap: "wrap", gap: 10 }}>
        <div>
          <div className="card-title">Network Attack Path Graph</div>
          <div className="card-subtitle" style={{ marginBottom: 0 }}>
            Expanded view of 40 nodes and 58 edges with anti-overlap word positioning
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <input
            type="text"
            placeholder="Search 40 nodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              padding: "6px 12px",
              fontSize: 12,
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              outline: "none"
            }}
          />
          <button
            className={`scenario-btn ${viewMode === "all" ? "active" : ""}`}
            style={{ padding: "6px 12px", fontSize: 12 }}
            onClick={() => setViewMode("all")}
          >
            All 40 Nodes
          </button>
          <button
            className={`scenario-btn ${viewMode === "attack_path" ? "active" : ""}`}
            style={{ padding: "6px 12px", fontSize: 12 }}
            onClick={() => setViewMode("attack_path")}
          >
            Attack Path Only
          </button>
        </div>
      </div>

      <div className="graph-canvas-box">
        <canvas ref={canvasRef} style={{ width: "100%", height: "100%", display: "block" }} />
      </div>

      {hoveredNode && (
        <div style={{
          marginTop: 10,
          padding: "10px 14px",
          background: "#ffffff",
          border: "1px solid #2563eb",
          borderRadius: 8,
          fontSize: 13,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          boxShadow: "0 2px 4px rgba(0,0,0,0.05)"
        }}>
          <div>
            <strong>{hoveredNode.name}</strong> ({hoveredNode.id}) — <span className="muted">{hoveredNode.unit}</span>
          </div>
          <div>
            Criticality: <span style={{ color: hoveredNode.criticality >= 4 ? "#dc2626" : "#2563eb", fontWeight: 700 }}>{hoveredNode.criticality}/5</span>
            {hoveredNode.record_count > 0 && ` | Records: ${hoveredNode.record_count.toLocaleString()}`}
          </div>
        </div>
      )}

      <div className="graph-legend-light">
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#dc2626" }}></div>
          <span>Start Asset (Entrypoint)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#ea580c" }}></div>
          <span>Traversal Hop</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#b91c1c" }}></div>
          <span>Target Database</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#0284c7" }}></div>
          <span>Critical System (&ge;4)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#64748b" }}></div>
          <span>Infrastructure Node</span>
        </div>
      </div>
    </div>
  );
}
