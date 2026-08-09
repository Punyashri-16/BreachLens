# BreachLens Frontend

BreachLens is a security analysis dashboard for visualizing blast radius, attack paths, and counterfactual remediation options when corporate assets are compromised.

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

## Backend Connection

This frontend is configured with a Vite proxy targeting `http://127.0.0.1:8000` (FastAPI backend):

- All API calls are routed through `/api/*` in `src/api/client.js`.
- Vite automatically rewrites `/api/graph` to `http://127.0.0.1:8000/graph`, `/api/scenarios` to `http://127.0.0.1:8000/scenarios`, etc.
- If the backend server is starting up or offline, `client.js` automatically uses a high-fidelity local fallback dataset containing the complete **40 nodes and 58 edges** network topology so the app is always functional.

## Features

1. **Scenario Picker**: Select from attack scenarios (`SC001` - `SC010`).
2. **Metric Cards**: Dynamic risk score out of 100, blast radius percentage, total records exposed, and critical asset count.
3. **Attack Path Step-by-Step Animation**: Reveals attack traversal step by step with MITRE ATT&CK technique tags.
4. **Interactive Attack Path Graph**: Renders the 40-node, 58-edge topology with animated attack vector flow lines, node halos, and hover details.
5. **Counterfactual Remediation Panel ("What to Fix First")**: Ranks high-impact fixes by score drop and system closure.
6. **Ask Bob Incident AI Assistant**: Natural language Q&A interface for analyzing attack paths.

## Git Ready

The repository is initialized and configured with `.gitignore` and modern Vite build scripts:

```bash
# Verify build output
npm run build
```
