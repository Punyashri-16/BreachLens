"""
Business risk calculation.

Turns a raw traversal result into the four numbers a business person
cares about: how bad is this, how far does it spread, what critical
systems are involved, and what does it mean commercially.
"""

# How much less a system matters per hop of distance.
# 0.7 means a system 2 hops away counts 70% as much as one 1 hop away,
# and 3 hops away counts 49%. An attacker CAN get there, but it takes
# more steps, more time, and there are more chances to detect them.
DISTANCE_DECAY = 0.7

# Criticality at or above this level counts as a critical asset.
CRITICAL_THRESHOLD = 4


def compute_risk_score(graph, reachable, start_asset_id):
    """
    A single 0 to 100 number.

    Every reachable asset contributes its criticality, reduced by how far
    away it sits. We divide by the theoretical worst case, which is every
    other asset in the company being reachable in a single hop.

    So 100 would mean total immediate compromise of everything, and a low
    score means the attacker is either boxed in or a long way from
    anything that matters.
    """
    if not reachable:
        return 0.0

    raw = sum(
        item["criticality"] * (DISTANCE_DECAY ** (item["hops"] - 1))
        for item in reachable
    )

    worst_case = sum(
        graph.nodes[node]["criticality"]
        for node in graph.nodes
        if node != start_asset_id
    )

    if worst_case == 0:
        return 0.0

    return round(min(100.0, raw / worst_case * 100), 1)


def compute_blast_radius(graph, reachable):
    """
    How much of the company the attacker can touch.

    Count and percentage, plus a breakdown by hop distance so the
    frontend can show how the compromise spreads outward.
    """
    total_others = graph.number_of_nodes() - 1
    count = len(reachable)

    by_hop = {}
    for item in reachable:
        by_hop[item["hops"]] = by_hop.get(item["hops"], 0) + 1

    return {
        "assets_reachable": count,
        "total_assets": total_others,
        "percentage": round(count / total_others * 100, 1) if total_others else 0.0,
        "by_hop": dict(sorted(by_hop.items())),
        "max_hops": max((i["hops"] for i in reachable), default=0),
    }


def identify_critical_assets(reachable):
    """
    The systems that would genuinely hurt to lose.

    Sorted by criticality first, then by how close they are, so the
    most severe and most immediately reachable appear at the top.
    """
    critical = [
        {
            "asset_id": item["asset_id"],
            "name": item["name"],
            "type": item["type"],
            "criticality": item["criticality"],
            "business_unit": item["business_unit"],
            "record_count": item.get("record_count", 0),
            "hops": item["hops"],
            "path": item["path"],
        }
        for item in reachable
        if item["criticality"] >= CRITICAL_THRESHOLD
    ]

    critical.sort(key=lambda a: (-a["criticality"], a["hops"]))
    return critical


def compute_business_impact(reachable):
    """
    What this means commercially.

    Total records exposed, which business units are affected, and the
    single worst asset reached. Records are the number that lands with
    non-technical people, because it maps to regulatory exposure.
    """
    total_records = sum(item.get("record_count", 0) for item in reachable)

    units = {}
    for item in reachable:
        unit = item["business_unit"]
        if unit not in units:
            units[unit] = {"business_unit": unit, "assets": 0, "records": 0}
        units[unit]["assets"] += 1
        units[unit]["records"] += item.get("record_count", 0)

    affected = sorted(units.values(), key=lambda u: -u["records"])

    data_assets = [i for i in reachable if i.get("record_count", 0) > 0]
    data_assets.sort(key=lambda i: -i["record_count"])

    worst = None
    if data_assets:
        top = data_assets[0]
        worst = {
            "asset_id": top["asset_id"],
            "name": top["name"],
            "record_count": top["record_count"],
            "hops": top["hops"],
        }

    return {
        "records_exposed": total_records,
        "data_stores_reached": len(data_assets),
        "business_units_affected": len(affected),
        "affected_units": affected,
        "highest_value_asset": worst,
    }


def assess(graph, bfs_result):
    """
    Run all four and return one dictionary.

    This is what POST /simulate calls.
    """
    reachable = bfs_result["reachable"]
    start = bfs_result["start_asset"]

    return {
        "risk_score": compute_risk_score(graph, reachable, start),
        "blast_radius": compute_blast_radius(graph, reachable),
        "critical_assets": identify_critical_assets(reachable),
        "business_impact": compute_business_impact(reachable),
    }