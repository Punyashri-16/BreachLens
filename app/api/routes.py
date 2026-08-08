"""
API routes.

All endpoints live here. The router is included by app/main.py.

Rule for every route: catch errors and return clean JSON. A bad request
must never take the server down mid-demo.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.database.connection import scenarios, incidents
from app.engine.graph_builder import build_graph
from app.engine.traversal import run_bfs, get_attack_path
from app.services.risk_service import assess
from app.services.mitre_service import summarise_techniques, map_path_to_techniques
from app.services.ai_service import generate_story, generate_recommendations
from app.services.bob_service import ask_bob
from app.services.counterfactual_service import analyse_counterfactuals
from app.models.schemas import (
    SimulateRequest,
    StoryRequest,
    RecommendationsRequest,
    BobRequest,
    CounterfactualRequest,
)

router = APIRouter()


# ==================================================================
# GET /graph
# ==================================================================
@router.get("/graph")
def get_graph():
    """
    The whole asset graph, ready for the frontend to draw.

    Returns a nodes list and an edges list. Most graph libraries in
    JavaScript expect exactly this shape.
    """
    try:
        graph = build_graph()

        nodes = [
            {
                "id": node_id,
                "name": attrs["name"],
                "type": attrs["type"],
                "criticality": attrs["criticality"],
                "business_unit": attrs["business_unit"],
                "record_count": attrs.get("record_count", 0),
                "is_critical": attrs["criticality"] >= 4,
                "holds_data": attrs.get("record_count", 0) > 0,
            }
            for node_id, attrs in graph.nodes(data=True)
        ]

        edges = [
            {
                "source": source,
                "target": target,
                "weight": attrs["weight"],
                "relationship_type": attrs["relationship_type"],
                "reason": attrs["reason"],
                "mitre_technique": attrs["mitre_technique"],
            }
            for source, target, attrs in graph.edges(data=True)
        ]

        type_counts = {}
        for n in nodes:
            type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1

        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "critical_nodes": sum(1 for n in nodes if n["is_critical"]),
                "total_records": sum(n["record_count"] for n in nodes),
                "by_type": type_counts,
            },
        }

    except Exception as error:
        print(f"GET /graph failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=500, detail="Could not build the graph")


# ==================================================================
# GET /scenarios
# ==================================================================
@router.get("/scenarios")
def list_scenarios():
    """All available scenarios, so the frontend can build a picker."""
    try:
        return {"scenarios": list(scenarios.find({}, {"_id": 0}))}
    except Exception as error:
        print(f"GET /scenarios failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=500, detail="Could not load scenarios")


# ==================================================================
# POST /simulate
# ==================================================================
@router.post("/simulate")
def simulate(request: SimulateRequest):
    """
    Run an attack simulation.

    Accepts either a scenario_id or a start_asset. Walks the graph from
    that point, computes the risk figures, maps the MITRE techniques,
    saves an incident record, and returns everything.
    """
    try:
        graph = build_graph()

        # ---------- work out where to start ----------
        scenario = None
        start_asset = request.start_asset

        if request.scenario_id:
            scenario = scenarios.find_one({"id": request.scenario_id}, {"_id": 0})
            if scenario is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario '{request.scenario_id}' does not exist",
                )
            start_asset = scenario["start_asset"]

        if not start_asset:
            raise HTTPException(
                status_code=400,
                detail="Provide either scenario_id or start_asset",
            )

        if start_asset not in graph:
            raise HTTPException(
                status_code=404,
                detail=f"Asset '{start_asset}' is not in the graph",
            )

        # ---------- walk the graph ----------
        bfs_result = run_bfs(graph, start_asset)

        # ---------- compute the business figures ----------
        risk = assess(graph, bfs_result)

        # ---------- map to MITRE ----------
        techniques = summarise_techniques(bfs_result["reachable"])

        # ---------- the headline path ----------
        data_assets = [
            r for r in bfs_result["reachable"] if r.get("record_count", 0) > 0
        ]
        data_assets.sort(key=lambda r: -r["record_count"])

        headline_path = None
        headline_techniques = []
        if data_assets:
            target = data_assets[0]["asset_id"]
            headline_path = get_attack_path(graph, start_asset, target)
            headline_techniques = map_path_to_techniques(headline_path)

        # ---------- assemble ----------
        result = {
            "scenario": scenario,
            "start_asset": start_asset,
            "start_asset_name": graph.nodes[start_asset]["name"],
            "reachable": bfs_result["reachable"],
            "total_reached": bfs_result["total_reached"],
            "risk_score": risk["risk_score"],
            "blast_radius": risk["blast_radius"],
            "critical_assets": risk["critical_assets"],
            "business_impact": risk["business_impact"],
            "mitre": techniques,
            "headline_path": headline_path,
            "headline_techniques": headline_techniques,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # ---------- save the incident ----------
        incident_doc = {
            "scenario_id": scenario["id"] if scenario else None,
            "scenario_name": scenario["name"] if scenario else "Ad hoc simulation",
            "start_asset": start_asset,
            "risk_score": risk["risk_score"],
            "assets_reachable": risk["blast_radius"]["assets_reachable"],
            "critical_assets_count": len(risk["critical_assets"]),
            "records_exposed": risk["business_impact"]["records_exposed"],
            "mitre_techniques": [
                t["technique_id"] for t in techniques.get("techniques", [])
            ],
            "created_at": datetime.now(timezone.utc),
        }

        inserted = incidents.insert_one(incident_doc)
        result["incident_id"] = str(inserted.inserted_id)

        return result

    except HTTPException:
        raise
    except Exception as error:
        print(f"POST /simulate failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=500, detail="Simulation failed")


# ==================================================================
# POST /counterfactual
# ==================================================================
@router.post("/counterfactual")
def counterfactual(request: CounterfactualRequest):
    """
    Which single connection should we cut first?

    For every edge the attacker can traverse, we remove it, re-run the
    whole analysis, and measure how far the risk score falls. Then we
    rank by biggest improvement.

    This is the endpoint that makes the product a decision tool rather
    than a display tool.
    """
    try:
        graph = build_graph()

        scenario = None
        start_asset = request.start_asset

        if request.scenario_id:
            scenario = scenarios.find_one({"id": request.scenario_id}, {"_id": 0})
            if scenario is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Scenario '{request.scenario_id}' does not exist",
                )
            start_asset = scenario["start_asset"]

        if not start_asset:
            raise HTTPException(
                status_code=400,
                detail="Provide either scenario_id or start_asset",
            )

        if start_asset not in graph:
            raise HTTPException(
                status_code=404,
                detail=f"Asset '{start_asset}' is not in the graph",
            )

        result = analyse_counterfactuals(graph, start_asset, request.limit)
        result["scenario"] = scenario
        return result

    except HTTPException:
        raise
    except Exception as error:
        print(f"POST /counterfactual failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=500, detail="Counterfactual analysis failed")


# ==================================================================
# POST /story
# ==================================================================
@router.post("/story")
def story(request: StoryRequest):
    """
    Narrate the incident as a sequence of events.

    Takes the simulation result returned by POST /simulate and passes it
    to the AI service. If the AI is unavailable, the service returns a
    factual narrative built from the computed numbers instead, so this
    endpoint never fails.
    """
    try:
        incident = request.incident

        if not incident:
            raise HTTPException(
                status_code=400,
                detail="Provide the simulation result in the 'incident' field",
            )

        # The headline path was already computed by /simulate, so we
        # reuse it rather than walking the graph again.
        attack_path = incident.get("headline_path")

        narrative = generate_story(incident, attack_path)

        return {
            "story": narrative,
            "scenario": incident.get("scenario", {}).get("name"),
            "start_asset": incident.get("start_asset"),
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"POST /story failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=500, detail="Could not generate the story")


# ==================================================================
# POST /recommendations
# ==================================================================
@router.post("/recommendations")
def recommendations(request: RecommendationsRequest):
    """
    Ranked remediation actions for this incident.

    Each action names a specific system from the simulation, so the
    output is tied to what was actually reachable rather than being a
    generic checklist.
    """
    try:
        incident = request.incident

        if not incident:
            raise HTTPException(
                status_code=400,
                detail="Provide the simulation result in the 'incident' field",
            )

        text = generate_recommendations(incident)

        # The AI returns a numbered list as one block of text. Split it
        # into an array so the frontend can render each action as its
        # own card instead of one wall of text.
        actions = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            cleaned = line
            if len(line) > 2 and line[0].isdigit():
                for sep in (". ", ") ", ".", ")"):
                    if sep in line[:4]:
                        cleaned = line.split(sep, 1)[1].strip()
                        break
            actions.append(cleaned)

        return {
            "recommendations": actions,
            "raw_text": text,
            "count": len(actions),
            "critical_assets_count": len(incident.get("critical_assets", [])),
        }

    except HTTPException:
        raise
    except Exception as error:
        print(f"POST /recommendations failed: {type(error).__name__}: {error}")
        raise HTTPException(
            status_code=500, detail="Could not generate recommendations"
        )


# ==================================================================
# POST /bob
# ==================================================================
@router.post("/bob")
def bob(request: BobRequest):
    """
    Answer a question about the current incident.

    The graph computes the facts. The AI only turns them into sentences.
    So when someone asks why the customer database is compromised, the
    path in the answer is the real path from our traversal, and it will
    match the graph if they check.
    """
    try:
        if not request.question or not request.question.strip():
            raise HTTPException(status_code=400, detail="Provide a question")

        if not request.incident:
            raise HTTPException(
                status_code=400,
                detail="Provide the simulation result in the 'incident' field",
            )

        return ask_bob(request.question, request.incident)

    except HTTPException:
        raise
    except Exception as error:
        print(f"POST /bob failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=500, detail="Could not answer the question")