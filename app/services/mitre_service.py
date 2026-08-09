from app.database.connection import mitre

_cache = None


def _get_lookup():
    global _cache
    if _cache is None:
        docs = list(mitre.find({}, {"_id": 0}))
        _cache = {doc["technique_id"]: doc for doc in docs}
    return _cache


def _lookup(technique_id):
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

    techniques.sort(key=lambda t: (-t["occurrences"], t["technique_id"]))

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