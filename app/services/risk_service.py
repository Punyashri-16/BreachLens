DISTANCE_DECAY = 0.7
CRITICAL_THRESHOLD = 4


def compute_risk_score(graph, reachable, start_asset_id):
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
    reachable = bfs_result["reachable"]
    start = bfs_result["start_asset"]

    return {
        "risk_score": compute_risk_score(graph, reachable, start),
        "blast_radius": compute_blast_radius(graph, reachable),
        "critical_assets": identify_critical_assets(reachable),
        "business_impact": compute_business_impact(reachable),
    }