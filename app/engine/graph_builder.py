"""
Graph builder.

Reads assets and edges out of MongoDB and turns them into a NetworkX
directed graph. Every other part of the engine works on the graph this
function returns, so this is the only place that touches the database.
"""

import networkx as nx

from app.database.connection import assets, edges


def build_graph():
    """
    Build the attack graph.

    Nodes are assets, carrying all of their fields as node attributes.
    Edges are lateral movement facts, carrying weight, relationship_type,
    reason and mitre_technique as edge attributes.

    Returns a networkx.DiGraph.
    """

    graph = nx.DiGraph()

    # ---------- NODES ----------
    # Exclude MongoDB's _id because it is an ObjectId and does not
    # convert to JSON when we send the graph to the frontend.
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

    # ---------- EDGES ----------
    edge_docs = list(edges.find({}, {"_id": 0}))
    skipped = []

    for edge in edge_docs:
        source = edge["source"]
        target = edge["target"]

        # An edge pointing at an asset that does not exist would create
        # a ghost node with no attributes, which breaks the risk service
        # later. Skip it and say so, rather than failing silently.
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
    """Return one asset's attributes as a dictionary, or None if absent."""
    if asset_id not in graph:
        return None
    return {"id": asset_id, **graph.nodes[asset_id]}