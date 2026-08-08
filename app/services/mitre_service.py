"""
MITRE ATT&CK mapping.

Every edge in the graph carries a technique id. These functions turn those
ids into full technique records, so the attack can be described in the
standard language a security team already uses.
"""

from app.database.connection import mitre


# The lookup table is small and never changes during a run, so we read it
# from MongoDB once and keep it in memory instead of querying per edge.
_cache = None


def _get_lookup():
    """Load all techniques into a dictionary keyed by technique id."""
    global _cache
    if _cache is None:
        docs = list(mitre.find({}, {"_id": 0}))
        _cache = {doc["technique_id"]: doc for doc in docs}
    return _cache


def _lookup(technique_id):
    """
    One technique record, or a placeholder if the id is not in the
    collection. Returning a placeholder rather than None means a missing
    entry shows up visibly in the UI instead of crashing it.
    """
    table = _get_lookup()
    if technique_id in table:
        return dict(table[technique_id])
    return {
        "technique_id": technique_id,
        "name": "Unknown technique",
        "tactic": "Unknown",
        "description": "This technique id is not present in the MITRE collection.",
    }


def map_path_to_techniques(attack_path):
    """
    The techniques used along one specific route, in order.

    Takes the output of get_attack_path() from the traversal module and
    returns one entry per step, so the frontend can label each hop of the
    path with the technique that made it possible.

    Returns an empty list if the path is None or has no steps.
    """
    if not attack_path or not attack_path.get("steps"):
        return []

    sequence = []
    for step in attack_path["steps"]:
        technique = _lookup(step["mitre_technique"])
        sequence.append({
            "step": step["step"],
            "from": step["from"],
            "from_name": step.get("from_name"),
            "to": step["to"],
            "to_name": step.get("to_name"),
            "relationship_type": step["relationship_type"],
            "technique_id": technique["technique_id"],
            "technique_name": technique["name"],
            "tactic": technique["tactic"],
            "description": technique["description"],
            "reason": step["reason"],
        })

    return sequence


def summarise_techniques(reachable):
    """
    Every unique technique involved in the whole simulation.

    Takes the reachable list from run_bfs(), where each item carries a
    reached_via block naming the technique that got the attacker there.
    Counts how often each technique appears and groups them by tactic.

    This is what lets the frontend say "this attack used 6 techniques
    across 4 tactics" rather than listing forty individual hops.
    """
    if not reachable:
        return {"techniques": [], "tactics": [], "total_techniques": 0}

    counts = {}
    for item in reachable:
        via = item.get("reached_via")
        if not via:
            continue
        tid = via.get("mitre_technique")
        if not tid:
            continue
        counts[tid] = counts.get(tid, 0) + 1

    techniques = []
    for tid, count in counts.items():
        technique = _lookup(tid)
        technique["occurrences"] = count
        techniques.append(technique)

    # Most-used first, so the dominant technique heads the list.
    techniques.sort(key=lambda t: (-t["occurrences"], t["technique_id"]))

    # Group by tactic. A tactic string may list several, as T1078 does,
    # so split on commas and count each one separately.
    tactic_counts = {}
    for t in techniques:
        for tactic in [x.strip() for x in t["tactic"].split(",")]:
            tactic_counts[tactic] = tactic_counts.get(tactic, 0) + 1

    tactics = [
        {"tactic": name, "technique_count": n}
        for name, n in sorted(tactic_counts.items(), key=lambda x: -x[1])
    ]

    return {
        "techniques": techniques,
        "tactics": tactics,
        "total_techniques": len(techniques),
    }