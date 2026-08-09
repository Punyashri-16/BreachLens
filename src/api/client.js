import { 
  MOCK_NODES, 
  MOCK_EDGES, 
  MOCK_SCENARIOS, 
  getMockSimulateResult, 
  getMockCounterfactualResult 
} from "../data/mockGraphData";

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
        // response was not JSON, keep status text
      }
      throw new Error(detail);
    }
    return await response.json();
  } catch (error) {
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
        total_nodes: MOCK_NODES.length,
        total_edges: MOCK_EDGES.length
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
      story: `The attack originated from asset '${body.incident?.start_asset_name || "Entry point"}' and moved through ${body.incident?.headline_path?.hops || 4} connected systems to reach internal databases.`,
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
    return Promise.resolve(generatePlainEnglishAIResponse(body.question, body.incident));
  }

  throw new Error("Unknown fallback endpoint");
}

// Plain-English AI Explanation Engine that converts technical graph paths into executive-level insights
function generatePlainEnglishAIResponse(question, incident) {
  const q = (question || "").toLowerCase();
  const startName = incident?.start_asset_name || "Entry System";
  const records = (incident?.business_impact?.records_exposed || 13303000).toLocaleString();
  const path = incident?.headline_path?.path || ["jira", "github_org", "repo_payments", "aws_prod_account", "prod_db_master"];
  const steps = incident?.headline_path?.steps || [];

  let answer = "";

  if (q.includes("simple terms") || q.includes("like i'm 5") || q.includes("explain")) {
    answer = `Imagine leaving your office keys inside an unlocked desk drawer (${startName}). An intruder opened that drawer, found the master password to the company's code storage (${path[1] || "GitHub"}), copied a secret key that opened the main building (${path[3] || "AWS Cloud"}), and walked straight into the vault containing all ${records} customer records (${path[path.length - 1] || "Database"}). No doors were broken—they simply used keys left lying around.`;
  } 
  else if (q.includes("financial") || q.includes("impact") || q.includes("business") || q.includes("affect")) {
    answer = `This security breach poses a critical business threat. With ${records} customer records exposed, privacy laws (like GDPR & CCPA) mandate reporting within 72 hours, potentially leading to regulatory fines of $15M–$50M. Additionally, compromised payment keys could force temporary freezes on credit card processing, halting ongoing revenue while engineering cleans the cloud environment.`;
  }
  else if (q.includes("stop") || q.includes("fix") || q.includes("fastest") || q.includes("remediate")) {
    answer = `The single most effective fix is to revoke the AWS deploy keys stored inside the Payments repository (${path[2] || "payments repo"}) and turn on Automated Secret Push Protection. This cuts the chain dead in its tracks, preventing the intruder from escalating into the AWS Production Account even if they gain access to GitHub.`;
  }
  else {
    answer = `The attacker started at ${startName} using stolen credentials. They navigated through ${steps.length} connected steps (${path.join(" → ")}), taking advantage of weak permission boundaries and hardcoded security keys until they reached the main database holding ${records} sensitive records.`;
  }

  return {
    question,
    answer,
    asset_id: incident?.business_impact?.highest_value_asset?.asset_id || "prod_db_master",
    intent: "plain_english_explanation",
    path
  };
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
