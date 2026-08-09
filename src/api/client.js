import { 
  MOCK_NODES, 
  MOCK_EDGES, 
  MOCK_SCENARIOS, 
  getMockSimulateResult, 
  getMockCounterfactualResult 
} from "../data/mockGraphData";

// The single place we talk to the backend.
// Every function returns parsed JSON or throws a readable error.
const BASE = "/api";

async function request(path, options = {}) {
  try {
    const response = await fetch(BASE + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!response.ok) {
      let detail = response.statusText;
      try {
        const body = await response.json();
        detail = body.detail || detail;
      } catch {
        // response was not JSON, keep the status text
      }
      throw new Error(detail);
    }
    return await response.json();
  } catch (error) {
    // If backend is not active, fallback to offline mock data matching exact backend contract
    if (error instanceof TypeError && error.message.includes("fetch")) {
      return getOfflineFallback(path, options);
    }
    throw error;
  }
}

function getOfflineFallback(path, options) {
  const body = options.body ? JSON.parse(options.body) : {};

  if (path === "/health") {
    return Promise.resolve({ status: "ok", mode: "offline_fallback" });
  }

  if (path === "/graph") {
    return Promise.resolve({
      stats: {
        total_nodes: MOCK_NODES.length, // 40
        total_edges: MOCK_EDGES.length  // 58
      },
      nodes: MOCK_NODES,
      edges: MOCK_EDGES
    });
  }

  if (path === "/scenarios") {
    return Promise.resolve({ scenarios: MOCK_SCENARIOS });
  }

  if (path === "/simulate") {
    return Promise.resolve(getMockSimulateResult(body.scenario_id));
  }

  if (path === "/counterfactual") {
    return Promise.resolve(getMockCounterfactualResult(body.scenario_id));
  }

  if (path === "/story") {
    return Promise.resolve({
      story: `The attacker initiated access via asset '${body.incident?.start_asset_name || "Entrypoint"}'. Traversing through ${body.incident?.headline_path?.hops || 4} hops, critical data repositories were exposed.`,
      scenario: body.incident?.scenario,
      start_asset: body.incident?.start_asset
    });
  }

  if (path === "/recommendations") {
    return Promise.resolve({
      recommendations: [
        "Enforce FIDO2 WebAuthn MFA across Okta and GitHub",
        "Enable GitHub Secret Scanning Push Protection to block hardcoded keys",
        "Restrict AWS IAM admin role assumption to JIT break-glass access"
      ],
      raw_text: "High priority remediations derived from graph traversal analysis.",
      count: 3,
      critical_assets_count: 2
    });
  }

  if (path === "/bob") {
    const q = (body.question || "").toLowerCase();
    let answer = `Based on incident ${body.incident?.incident_id || "analysis"}, the attack path progresses through ${body.incident?.headline_path?.path?.join(" → ") || "network nodes"}.`;
    
    if (q.includes("customer database") || q.includes("compromised") || q.includes("why")) {
      answer = "The customer database was reached because a developer account was compromised on Jira, leading to leaked OAuth tokens in GitHub. Hardcoded AWS credentials in the payments repository were then used to assume the AWS Admin IAM role and access the production database master.";
    } else if (q.includes("blast radius") || q.includes("how far")) {
      answer = `The blast radius reaches ${body.incident?.blast_radius?.percentage || 89.7}% of the total estate, compromising ${body.incident?.blast_radius?.assets_reachable || 35} out of ${body.incident?.blast_radius?.total_assets || 39} assets within ${body.incident?.blast_radius?.max_hops || 6} hops.`;
    }

    return Promise.resolve({
      question: body.question,
      answer,
      asset_id: body.incident?.business_impact?.highest_value_asset?.asset_id || "prod_db_master",
      intent: "path_explanation",
      path: body.incident?.headline_path?.path || []
    });
  }

  throw new Error("Unknown fallback endpoint");
}

export function getHealth() {
  return request("/health");
}

export function getGraph() {
  return request("/graph");
}

export function getScenarios() {
  return request("/scenarios");
}

export function simulate(scenarioId) {
  return request("/simulate", {
    method: "POST",
    body: JSON.stringify({ scenario_id: scenarioId }),
  });
}

export function getCounterfactual(scenarioId, limit = 5) {
  return request("/counterfactual", {
    method: "POST",
    body: JSON.stringify({ scenario_id: scenarioId, limit }),
  });
}

export function getStory(incident) {
  return request("/story", {
    method: "POST",
    body: JSON.stringify({ incident }),
  });
}

export function getRecommendations(incident) {
  return request("/recommendations", {
    method: "POST",
    body: JSON.stringify({ incident }),
  });
}

export function askBob(question, incident) {
  return request("/bob", {
    method: "POST",
    body: JSON.stringify({ question, incident }),
  });
}
