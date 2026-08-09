from collections import deque


def run_bfs(graph, start_asset_id, max_hops=None):
    if start_asset_id not in graph:
        return {
            "start_asset": start_asset_id,
            "reachable": [],
            "total_reached": 0,
            "error": f"Asset '{start_asset_id}' is not in the graph",
        }

    visited = {start_asset_id: [start_asset_id]}

    queue = deque([(start_asset_id, 0)])

    reachable = []

    while queue:
        current, hops = queue.popleft()

        if max_hops is not None and hops >= max_hops:
            continue

        for neighbour in graph.successors(current):

            if neighbour in visited:
                continue

            path = visited[current] + [neighbour]
            visited[neighbour] = path

            node = graph.nodes[neighbour]
            edge = graph.edges[current, neighbour]

            reachable.append({
                "asset_id": neighbour,
                "name": node["name"],
                "type": node["type"],
                "criticality": node["criticality"],
                "business_unit": node["business_unit"],
                "record_count": node.get("record_count", 0),
                "hops": hops + 1,
                "path": path,
                "reached_via": {
                    "from": current,
                    "relationship_type": edge["relationship_type"],
                    "reason": edge["reason"],
                    "mitre_technique": edge["mitre_technique"],
                },
            })

            queue.append((neighbour, hops + 1))

    reachable.sort(key=lambda r: (r["hops"], r["asset_id"]))

    return {
        "start_asset": start_asset_id,
        "start_asset_name": graph.nodes[start_asset_id]["name"],
        "reachable": reachable,
        "total_reached": len(reachable),
    }


def get_attack_path(graph, start_asset_id, target_asset_id):
    if start_asset_id not in graph or target_asset_id not in graph:
        return None

    result = run_bfs(graph, start_asset_id)

    match = next(
        (r for r in result["reachable"] if r["asset_id"] == target_asset_id),
        None,
    )
    if match is None:
        return None

    path = match["path"]

    steps = []
    for i in range(len(path) - 1):
        source, target = path[i], path[i + 1]
        edge = graph.edges[source, target]
        steps.append({
            "step": i + 1,
            "from": source,
            "from_name": graph.nodes[source]["name"],
            "to": target,
            "to_name": graph.nodes[target]["name"],
            "relationship_type": edge["relationship_type"],
            "weight": edge["weight"],
            "reason": edge["reason"],
            "mitre_technique": edge["mitre_technique"],
        })

    return {
        "start_asset": start_asset_id,
        "target_asset": target_asset_id,
        "hops": match["hops"],
        "path": path,
        "steps": steps,
    }