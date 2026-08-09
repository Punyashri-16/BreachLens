import networkx as nx

from app.database.connection import assets, edges


def build_graph():
    graph = nx.DiGraph()
    asset_docs = list(assets.find({}, {"_id": 0}))

    for asset in asset_docs:
        graph.add_node(
            asset["id"],
            name=asset["name"],
            type=asset["type"],
            criticality=asset["criticality"],
            business_unit=asset["business_unit"],
            record_count=asset.get("record_count", 0),
        )

    edge_docs = list(edges.find({}, {"_id": 0}))
    skipped = []

    for edge in edge_docs:
        source = edge["source"]
        target = edge["target"]

        if source not in graph or target not in graph:
            skipped.append(f"{source} -> {target}")
            continue

        graph.add_edge(
            source,
            target,
            weight=edge["weight"],
            relationship_type=edge["relationship_type"],
            reason=edge["reason"],
            mitre_technique=edge["mitre_technique"],
        )

    if skipped:
        print(f"WARNING: skipped {len(skipped)} edge(s) referencing missing assets:")
        for s in skipped:
            print("  -", s)

    print(f"Graph built: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    return graph


def get_node(graph, asset_id):
    if asset_id not in graph:
        return None
    return {"id": asset_id, **graph.nodes[asset_id]}