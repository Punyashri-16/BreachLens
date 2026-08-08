"""
Counterfactual analysis.

A counterfactual is a "what if things were different" question. Here we
ask it once per edge:

    "If this one connection did not exist, how much safer would we be?"

We answer it by actually removing the edge and re-running the whole
analysis, then measuring how far the risk score fell. Nothing is
estimated. Every number came from running the real engine on a real
modified graph.

Why this matters: other tools tell you what is wrong. This tells you
what to FIX FIRST, with a number attached. That turns the product from
something that displays information into something that decides.
"""

from app.engine.traversal import run_bfs
from app.services.risk_service import assess


def _collect_candidate_edges(reachable):
    """
    Work out which edges are worth testing.

    Only edges the attacker can actually traverse matter. An edge in a
    far corner of the company is irrelevant to this incident, and
    testing it would waste a full traversal for a guaranteed zero.

    Every reachable asset carries the path taken to reach it, so we walk
    each path in consecutive pairs and collect the edges used.

        path ["jira", "github_org", "repo_payments"]
        gives  jira -> github_org  and  github_org -> repo_payments

    A set is used because many paths share their early edges.
    """
    candidates = set()
    for item in reachable:
        path = item.get("path", [])
        for i in range(len(path) - 1):
            candidates.add((path[i], path[i + 1]))
    return sorted(candidates)


def analyse_counterfactuals(graph, start_asset_id, limit=10):
    """Rank every reachable edge by how much removing it would help."""

    if start_asset_id not in graph:
        return {
            "start_asset": start_asset_id,
            "error": f"Asset '{start_asset_id}' is not in the graph",
            "recommendations": [],
        }

    # ---------- 1. BASELINE ----------
    # What the world looks like now, before we change anything.
    base_bfs = run_bfs(graph, start_asset_id)
    base_risk = assess(graph, base_bfs)

    base_score = base_risk["risk_score"]
    base_reachable = base_bfs["total_reached"]
    base_critical = len(base_risk["critical_assets"])
    base_records = base_risk["business_impact"]["records_exposed"]

    # ---------- 2. CANDIDATES ----------
    candidates = _collect_candidate_edges(base_bfs["reachable"])
    results = []

    for source, target in candidates:
        if not graph.has_edge(source, target):
            continue

        edge_data = graph.edges[source, target]

        # ---------- 3. THE COUNTERFACTUAL WORLD ----------
        # Copy the graph and delete this one connection. We copy rather
        # than remove-and-restore so the original is never mutated.
        modified = graph.copy()
        modified.remove_edge(source, target)

        # ---------- 4. RE-RUN THE REAL ENGINE ----------
        # Same traversal, same scoring. The only difference in this
        # world is the missing edge.
        new_bfs = run_bfs(modified, start_asset_id)
        new_risk = assess(modified, new_bfs)

        new_score = new_risk["risk_score"]
        new_reachable = new_bfs["total_reached"]
        new_critical = len(new_risk["critical_assets"])
        new_records = new_risk["business_impact"]["records_exposed"]

        # ---------- 5. MEASURE THE DIFFERENCE ----------
        drop = round(base_score - new_score, 1)
        percent_drop = round(drop / base_score * 100, 1) if base_score > 0 else 0.0

        before_ids = {r["asset_id"] for r in base_bfs["reachable"]}
        after_ids = {r["asset_id"] for r in new_bfs["reachable"]}
        closed_ids = sorted(before_ids - after_ids)

        results.append({
            "source": source,
            "source_name": graph.nodes[source]["name"],
            "target": target,
            "target_name": graph.nodes[target]["name"],
            "relationship_type": edge_data["relationship_type"],
            "reason": edge_data["reason"],
            "mitre_technique": edge_data["mitre_technique"],
            "weight": edge_data["weight"],

            "baseline_score": base_score,
            "new_score": new_score,
            "drop": drop,
            "percent_drop": percent_drop,

            "assets_closed": base_reachable - new_reachable,
            "critical_assets_closed": base_critical - new_critical,
            "records_protected": base_records - new_records,
            "closed_asset_ids": closed_ids,

            # An edge whose removal changes nothing is still a finding.
            # It means another route already exists, so revoking this
            # access would give a false sense of safety.
            "no_effect": drop <= 0 and (base_reachable - new_reachable) == 0,
        })

    # ---------- 6. RANK ----------
    results.sort(key=lambda r: (-r["drop"], -r["assets_closed"], r["source"]))

    return {
        "start_asset": start_asset_id,
        "start_asset_name": graph.nodes[start_asset_id]["name"],
        "baseline_score": base_score,
        "baseline_assets_reachable": base_reachable,
        "baseline_critical_assets": base_critical,
        "baseline_records_exposed": base_records,
        "edges_tested": len(results),
        "recommendations": results[:limit],
    }