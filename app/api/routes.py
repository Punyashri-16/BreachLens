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


@router.get("/graph")
def get_graph():
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


@router.get("/scenarios")
def list_scenarios():
    try:
        return {"scenarios": list(scenarios.find({}, {"_id": 0}))}
    except Exception as error:
        print(f"GET /scenarios failed: {type(error).__name__}: {error}")
        raise HTTPException(status_code=500, detail="Could not load scenarios")


@router.post("/simulate")
def simulate(request: SimulateRequest):
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

        bfs_result = run_bfs(graph, start_asset)

        risk = assess(graph, bfs_result)

        techniques = summarise_techniques(bfs_result["reachable"])
        attack_edges = []
        seen = set()
        for item in bfs_result["reachable"]:
            p = item["path"]
            for i in range(len(p) - 1):
                pair = (p[i], p[i + 1])
                if pair in seen:
                    continue
                seen.add(pair)
                edge = graph.edges[p[i], p[i + 1]]
                attack_edges.append({
                    "id": f"{p[i]}--{p[i+1]}",
                    "source": p[i],
                    "target": p[i + 1],
                    "relationship_type": edge["relationship_type"],
                    "mitre_technique": edge["mitre_technique"],
                    "reason": edge["reason"],
                })

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

        result = {
            "scenario": scenario,
            "start_asset": start_asset,
            "start_asset_name": graph.nodes[start_asset]["name"],
            "reachable": bfs_result["reachable"],
            "attack_edges": attack_edges,
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


@router.post("/counterfactual")
def counterfactual(request: CounterfactualRequest):
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


@router.post("/story")
def story(request: StoryRequest):
    try:
        incident = request.incident

        if not incident:
            raise HTTPException(
                status_code=400,
                detail="Provide the simulation result in the 'incident' field",
            )

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


@router.post("/recommendations")
def recommendations(request: RecommendationsRequest):
    try:
        incident = request.incident

        if not incident:
            raise HTTPException(
                status_code=400,
                detail="Provide the simulation result in the 'incident' field",
            )

        text = generate_recommendations(incident)

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


@router.post("/bob")
def bob(request: BobRequest):
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