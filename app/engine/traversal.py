"""
Graph traversal.

This is the heart of the project. It answers the question:
"if an attacker controls this one asset, what else can they reach?"

Nothing here is scripted. The attack paths come out of walking the graph
over facts that were seeded independently of each other.
"""

from collections import deque


def run_bfs(graph, start_asset_id, max_hops=None):
    """
    Breadth-first search outward from one asset.

    BFS explores in rings: everything one hop away, then everything two
    hops away, and so on. Because it moves outward evenly, the first time
    it arrives at a node it has arrived by the shortest route, so hop
    counts are correct without any extra work.

    Returns a dictionary containing the start asset, the list of reachable
    assets with their hop count and path, and the total count.
    """

    # An unknown start id returns an empty result rather than raising,
    # so a bad request cannot take the API down.
    if start_asset_id not in graph:
        return {
            "start_asset": start_asset_id,
            "reachable": [],
            "total_reached": 0,
            "error": f"Asset '{start_asset_id}' is not in the graph",
        }

    # visited maps each node to the path taken to reach it.
    visited = {start_asset_id: [start_asset_id]}

    # deque holds (node, hop count). popleft() takes from the front,
    # which is what makes this breadth-first rather than depth-first.
    queue = deque([(start_asset_id, 0)])

    reachable = []

    while queue:
        current, hops = queue.popleft()

        if max_hops is not None and hops >= max_hops:
            continue

        for neighbour in graph.successors(current):

            # Already seen means we already reached it by a shorter or
            # equal route, so skip it. This is also what stops cycles
            # from looping forever.
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

    # Nearest first, so the frontend can animate outward naturally.
    reachable.sort(key=lambda r: (r["hops"], r["asset_id"]))

    return {
        "start_asset": start_asset_id,
        "start_asset_name": graph.nodes[start_asset_id]["name"],
        "reachable": reachable,
        "total_reached": len(reachable),
    }


def get_attack_path(graph, start_asset_id, target_asset_id):
    """
    The specific route from one asset to another, step by step.

    Used by the /bob endpoint. When a judge asks why the customer
    database is compromised, this returns the real path, and the AI
    only puts it into sentences.

    Returns None if no path exists.
    """

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

    # Turn the list of node ids into a list of steps carrying the
    # mechanism and MITRE technique used at each hop.
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