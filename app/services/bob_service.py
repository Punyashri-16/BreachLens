"""
Bob — the question answering service.

The important idea: the backend computes the facts, the AI only explains
them. When someone asks "why is the customer database compromised?", the
path in the answer is the real path from the graph, not something the
model made up.

Flow:
  question text  ->  work out which asset it is about
                 ->  compute the real answer from the graph
                 ->  give both to the AI and ask it to explain
"""

import re

from app.engine.graph_builder import build_graph
from app.engine.traversal import get_attack_path
from app.services.mitre_service import map_path_to_techniques
from app.ai.client import generate


# Words that signal what kind of question this is.
INTENT_WORDS = {
    "path": ["how", "why", "reach", "reached", "get to", "access", "compromis", "route", "path"],
    "risk": ["risk", "score", "how bad", "severity", "serious"],
    "impact": ["impact", "records", "data", "business", "cost", "customer"],
    "fix": ["fix", "stop", "prevent", "remediat", "should we", "recommend", "protect"],
    "spread": ["spread", "blast", "how many", "how far", "reach"],
}


def _find_asset(graph, question):
    """
    Work out which asset the question is about.

    Checks full names first ("Customer Database"), then asset ids
    ("customer_db"), then the id with underscores as spaces.
    Returns the asset id, or None if no asset is mentioned.
    """
    text = question.lower()
    matches = []

    for asset_id in graph.nodes:
        name = graph.nodes[asset_id]["name"].lower()
        loose = asset_id.replace("_", " ").lower()

        if name in text:
            matches.append((asset_id, len(name)))
        elif asset_id.lower() in text:
            matches.append((asset_id, len(asset_id)))
        elif loose in text:
            matches.append((asset_id, len(loose)))

    if not matches:
        return None

    # Longest match wins, so "customer database" beats "database".
    matches.sort(key=lambda m: -m[1])
    return matches[0][0]


def _find_intent(question):
    """Classify the question. Defaults to 'path'."""
    text = question.lower()
    for intent, words in INTENT_WORDS.items():
        if any(w in text for w in words):
            return intent
    return "path"


def _compute_facts(graph, question, incident):
    """
    Build the factual answer from the graph. No AI here at all.
    Returns a dictionary of facts plus a readable text block.
    """
    start = incident.get("start_asset")
    reachable = incident.get("reachable", [])
    asset_id = _find_asset(graph, question)
    intent = _find_intent(question)

    facts = {"intent": intent, "asset_id": asset_id, "path": None}
    lines = [
        f"Entry point: {incident.get('start_asset_name', start)}",
        f"Risk score: {incident.get('risk_score', 0)} out of 100",
        f"Systems reachable: {incident.get('blast_radius', {}).get('assets_reachable', 0)} "
        f"of {incident.get('blast_radius', {}).get('total_assets', 0)}",
        f"Records exposed: {incident.get('business_impact', {}).get('records_exposed', 0):,}",
    ]

    # If a specific asset was named, compute the real path to it.
    if asset_id and start:
        entry = next((r for r in reachable if r["asset_id"] == asset_id), None)

        if entry is None:
            lines.append(
                f"\n{graph.nodes[asset_id]['name']} is NOT reachable in this incident."
            )
            facts["reachable"] = False
        else:
            path = get_attack_path(graph, start, asset_id)
            facts["path"] = path
            facts["reachable"] = True

            node = graph.nodes[asset_id]
            lines.append(
                f"\nAbout {node['name']}:"
                f"\n  Criticality: {node['criticality']} out of 5"
                f"\n  Business unit: {node['business_unit']}"
                f"\n  Records held: {node.get('record_count', 0):,}"
                f"\n  Distance from entry: {entry['hops']} steps"
            )

            if path and path.get("steps"):
                lines.append("\nThe exact route the attacker takes:")
                for s in path["steps"]:
                    lines.append(
                        f"  Step {s['step']}: {s['from_name']} to {s['to_name']} "
                        f"({s['mitre_technique']}) because {s['reason']}"
                    )

                techniques = map_path_to_techniques(path)
                facts["techniques"] = techniques
                names = ", ".join(
                    f"{t['technique_id']} {t['technique_name']}" for t in techniques
                )
                lines.append(f"\nTechniques used along this route: {names}")

    # Extra context depending on what was asked.
    if intent in ("fix", "path") and incident.get("critical_assets"):
        lines.append("\nMost critical systems reached:")
        for c in incident["critical_assets"][:5]:
            via = c["path"][-2] if len(c["path"]) >= 2 else c["path"][0]
            lines.append(
                f"  {c['name']} (criticality {c['criticality']}, "
                f"{c['hops']} steps, reached from {via})"
            )

    if intent == "impact" and incident.get("business_impact", {}).get("affected_units"):
        lines.append("\nBusiness units affected:")
        for u in incident["business_impact"]["affected_units"][:5]:
            lines.append(
                f"  {u['business_unit']}: {u['assets']} systems, {u['records']:,} records"
            )

    facts["text"] = "\n".join(lines)
    return facts


def _fallback_answer(facts, question):
    """
    A plain answer built straight from the computed facts, used when the
    AI is unavailable. Less fluent, but completely correct.
    """
    if facts.get("reachable") is False:
        return "That system is not reachable in this incident."

    path = facts.get("path")
    if path and path.get("steps"):
        steps = " ".join(
            f"Step {s['step']}: {s['from_name']} leads to {s['to_name']} because "
            f"{s['reason'].lower()}."
            for s in path["steps"]
        )
        return (
            f"It is reachable in {path['hops']} steps from the entry point. {steps}"
        )

    return facts["text"]


def ask_bob(question, incident):
    """
    Answer a question about the current incident.

    The graph produces the facts. The model only turns them into
    sentences. If the model is unavailable, the factual answer is
    returned directly.
    """
    if not question or not question.strip():
        return {
            "question": question,
            "answer": "Please ask a question about this incident.",
            "asset_id": None,
            "path": None,
        }

    graph = build_graph()
    facts = _compute_facts(graph, question, incident)

    prompt = f"""You are a security analyst answering a question about an incident.

The question:
{question}

These are the computed facts. They come from our attack graph and they are correct:

{facts['text']}

Answer the question in 2 to 4 sentences.

Rules:
- Use only the facts above. Do not invent systems, numbers or steps.
- If a route is given, walk through it in order and explain why each step works.
- Write plainly. Explain any technical term in the same sentence.
- Do not use bullet points or headings. Answer directly, no preamble.
"""

    answer = generate(
        prompt,
        temperature=0.3,
        fallback=_fallback_answer(facts, question),
    )

    return {
        "question": question,
        "answer": answer,
        "asset_id": facts.get("asset_id"),
        "intent": facts.get("intent"),
        "path": facts.get("path"),
    }