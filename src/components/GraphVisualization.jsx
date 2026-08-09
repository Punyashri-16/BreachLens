import React, { useRef, useEffect, useState } from "react";
import { MOCK_NODES, MOCK_EDGES } from "../data/mockGraphData";

// Categorized 6 Tier Zones for the 40 nodes to ensure wide spacing and zero label overlap
const TIER_CONFIG = {
  perimeter: { zone: "1. Perimeter & Entry", yRatio: 0.12, icon: "🛡️" },
  endpoint: { zone: "1. Perimeter & Entry", yRatio: 0.14, icon: "💻" },
  saas: { zone: "2. Identity & SaaS", yRatio: 0.28, icon: "🔑" },
  iam: { zone: "2. Identity & SaaS", yRatio: 0.30, icon: "🔒" },
  scm: { zone: "3. Repos & DevOps", yRatio: 0.46, icon: "📁" },
  code: { zone: "3. Repos & DevOps", yRatio: 0.48, icon: "💻" },
  devops: { zone: "3. Repos & DevOps", yRatio: 0.50, icon: "⚙️" },
  compute: { zone: "4. Cloud & Infrastructure", yRatio: 0.66, icon: "🖥️" },
  cloud: { zone: "4. Cloud & Infrastructure", yRatio: 0.68, icon: "☁️" },
  secret: { zone: "4. Cloud & Infrastructure", yRatio: 0.70, icon: "🔐" },
  database: { zone: "5. Data Stores & Backups", yRatio: 0.86, icon: "🗄️" },
  storage: { zone: "5. Data Stores & Backups", yRatio: 0.88, icon: "📦" },
  monitoring: { zone: "5. Data Stores & Backups", yRatio: 0.90, icon: "📊" }
};

export default function GraphVisualization({ result, graphData }) {
  const canvasRef = useRef(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [viewMode, setViewMode] = useState("all"); // "all" | "attack_path"

  const nodes = graphData?.nodes || MOCK_NODES;
  const edges = graphData?.edges || MOCK_EDGES;

  // Active attack path sequence from simulation result
  const activePathIds = result?.headline_path?.path || [];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");

    // High DPI crisp canvas scaling
    const rect = canvas.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    canvas.width = width * window.devicePixelRatio;
    canvas.height = height * window.devicePixelRatio;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

    // Calculate node coordinates with staggered offset to eliminate label overlap completely
    const nodePos = {};
    
    // Group nodes by their tier
    const groups = {};
    nodes.forEach(n => {
      const tierKey = n.type || "compute";
      if (!groups[tierKey]) groups[tierKey] = [];
      groups[tierKey].push(n);
    });

    // Compute coordinates with horizontal padding and vertical offset staggering
    Object.keys(groups).forEach(tierKey => {
      const groupNodes = groups[tierKey];
      const cfg = TIER_CONFIG[tierKey] || { yRatio: 0.5, icon: "📌" };
      const baseY = cfg.yRatio * height;

      groupNodes.forEach((node, idx) => {
        const spacing = (width - 120) / (groupNodes.length + 1);
        // Stagger Y slightly between odd and even nodes in the same tier
        const yOffset = (idx % 2 === 0 ? -16 : 16);
        nodePos[node.id] = {
          x: 60 + spacing * (idx + 1),
          y: Math.max(35, Math.min(height - 40, baseY + yOffset)),
          labelPosition: idx % 2 === 0 ? "top" : "bottom",
          icon: cfg.icon,
          node
        };
      });
    });

    let animationFrameId;
    let pulseTime = 0;

    const render = () => {
      pulseTime += 0.05;
      ctx.clearRect(0, 0, width, height);

      // Draw subtle dark sapphire grid
      ctx.strokeStyle = "rgba(30, 41, 59, 0.4)";
      ctx.lineWidth = 1;
      for (let x = 0; x < width; x += 50) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }
      for (let y = 0; y < height; y += 50) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }

      // Draw zone divider markers
      const zones = [
        { name: "Perimeter & Endpoints", y: 0.08 * height },
        { name: "Identity & SaaS Services", y: 0.24 * height },
        { name: "Repositories & CI/CD Pipelines", y: 0.42 * height },
        { name: "Cloud Accounts & Compute Infrastructure", y: 0.62 * height },
        { name: "Databases, Storage & Backups", y: 0.82 * height }
      ];

      ctx.font = "600 11px system-ui";
      ctx.fillStyle = "rgba(148, 163, 184, 0.4)";
      zones.forEach(z => {
        ctx.fillText(z.name.toUpperCase(), 16, z.y);
      });

      // Draw edges (58 connections)
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
          ctx.strokeStyle = "#ef4444";
          ctx.lineWidth = 2.5;
          ctx.setLineDash([8, 4]);
          ctx.lineDashOffset = -pulseTime * 12;
        } else {
          ctx.strokeStyle = "rgba(51, 65, 85, 0.35)";
          ctx.lineWidth = 1;
          ctx.setLineDash([]);
        }
        ctx.stroke();
        ctx.setLineDash([]);

        // Animated flow particles along active attack path edges
        if (isPathEdge) {
          const progress = (pulseTime * 0.4) % 1;
          const px = src.x + (tgt.x - src.x) * progress;
          const py = src.y + (tgt.y - src.y) * progress;

          ctx.beginPath();
          ctx.arc(px, py, 4, 0, Math.PI * 2);
          ctx.fillStyle = "#ff8888";
          ctx.fill();
        }
      });

      // Draw nodes (40 infrastructure assets)
      nodes.forEach(n => {
        const pos = nodePos[n.id];
        if (!pos) return;

        const isActivePath = activePathIds.includes(n.id);
        const isStartNode = activePathIds[0] === n.id;
        const isTargetNode = activePathIds[activePathIds.length - 1] === n.id;

        if (viewMode === "attack_path" && !isActivePath) return;

        // Animated glowing halo for active attack path nodes
        if (isActivePath) {
          const haloRadius = 14 + Math.sin(pulseTime * 3) * 3;
          ctx.beginPath();
          ctx.arc(pos.x, pos.y, haloRadius, 0, Math.PI * 2);
          ctx.fillStyle = isStartNode || isTargetNode ? "rgba(239, 68, 68, 0.3)" : "rgba(249, 115, 22, 0.25)";
          ctx.fill();
        }

        // Inner node body
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 8, 0, Math.PI * 2);

        if (isStartNode) {
          ctx.fillStyle = "#ef4444"; // Bright red for attack origin
        } else if (isTargetNode) {
          ctx.fillStyle = "#dc2626"; // Deep red for compromised target
        } else if (isActivePath) {
          ctx.fillStyle = "#f97316"; // Hop orange
        } else if (n.criticality >= 4) {
          ctx.fillStyle = "#3b82f6"; // Critical asset electric blue
        } else {
          ctx.fillStyle = "#475569"; // Standard node slate
        }

        ctx.fill();
        ctx.strokeStyle = "#0f172a";
        ctx.lineWidth = 2;
        ctx.stroke();

        // Render clean label badge with staggered placement to prevent overlapping
        const labelText = n.name || n.id;
        ctx.font = isActivePath ? "bold 11px system-ui" : "10px system-ui";
        const textWidth = ctx.measureText(labelText).width;

        const ly = pos.labelPosition === "top" ? pos.y - 14 : pos.y + 22;

        // Background pill behind label for 100% legibility
        ctx.fillStyle = isActivePath ? "rgba(15, 23, 42, 0.9)" : "rgba(15, 23, 42, 0.75)";
        ctx.beginPath();
        ctx.roundRect(pos.x - textWidth / 2 - 4, ly - 10, textWidth + 8, 14, 4);
        ctx.fill();
        ctx.strokeStyle = isActivePath ? (isStartNode ? "#ef4444" : "#f97316") : "#1e293b";
        ctx.lineWidth = 1;
        ctx.stroke();

        // Label text
        ctx.fillStyle = isActivePath ? "#ffffff" : "#cbd5e1";
        ctx.textAlign = "center";
        ctx.fillText(labelText, pos.x, ly);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    // Interactive mouse movement for node tooltips
    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let found = null;
      Object.values(nodePos).forEach(pos => {
        const dx = mx - pos.x;
        const dy = my - pos.y;
        if (dx * dx + dy * dy <= 144) {
          found = { ...pos.node, icon: pos.icon };
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
          <div style={{ fontSize: 15, fontWeight: 600, color: "#f8fafc" }}>
            Network Topology & Attack Traversal Graph
          </div>
          <div className="muted" style={{ fontSize: 12.5 }}>
            Interactive 2D graph of all {nodes.length} infrastructure assets and {edges.length} attack vectors
          </div>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            style={{ fontSize: 12, padding: "5px 12px" }}
            className={viewMode === "all" ? "active" : ""}
            onClick={() => setViewMode("all")}
          >
            All 40 Nodes
          </button>
          <button
            style={{ fontSize: 12, padding: "5px 12px" }}
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
          marginTop: 12,
          padding: "10px 14px",
          background: "#0b1120",
          border: "1px solid #3b82f6",
          borderRadius: 8,
          fontSize: 13,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}>
          <div>
            <span>{hoveredNode.icon} <strong>{hoveredNode.name}</strong></span> ({hoveredNode.id}) — <span className="muted">{hoveredNode.unit}</span>
          </div>
          <div style={{ fontSize: 12.5 }}>
            Criticality: <span style={{ color: hoveredNode.criticality >= 4 ? "#ef4444" : "#60a5fa", fontWeight: 600 }}>{hoveredNode.criticality}/5</span>
            {hoveredNode.record_count > 0 && ` | Records Exposed: ${hoveredNode.record_count.toLocaleString()}`}
          </div>
        </div>
      )}

      <div className="graph-legend">
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#ef4444" }}></div>
          <span>Attack Start (Entrypoint)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#f97316" }}></div>
          <span>Traversal Hop</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#dc2626" }}></div>
          <span>Compromised Data Target</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#3b82f6" }}></div>
          <span>Critical System (&ge;4)</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: "#475569" }}></div>
          <span>Infrastructure Node</span>
        </div>
      </div>
    </div>
  );
}
