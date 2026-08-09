from app.database.connection import assets, edges, mitre, scenarios, check_connection

from app.seed.assets_data import ASSETS
from app.seed.edges_data import EDGES
from app.seed.mitre_data import MITRE_TECHNIQUES
from app.seed.scenarios_data import SCENARIOS


def validate():
    asset_ids = {a["id"] for a in ASSETS}
    technique_ids = {m["technique_id"] for m in MITRE_TECHNIQUES}
    problems = []

    if len(asset_ids) != len(ASSETS):
        problems.append("Duplicate asset ids found")

    for e in EDGES:
        if e["source"] not in asset_ids:
            problems.append(f"Edge source does not exist: {e['source']}")
        if e["target"] not in asset_ids:
            problems.append(f"Edge target does not exist: {e['target']}")
        if e["mitre_technique"] not in technique_ids:
            problems.append(f"Unknown MITRE technique: {e['mitre_technique']}")
        if not (0 < e["weight"] <= 1):
            problems.append(f"Weight out of range on {e['source']} -> {e['target']}")

    for s in SCENARIOS:
        if s["start_asset"] not in asset_ids:
            problems.append(f"Scenario {s['id']} starts at unknown asset: {s['start_asset']}")

    if problems:
        print("\nSeed data is invalid. Nothing was written.\n")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)

    print("Validation passed.")


def run_seed():
    """Clear the four reference collections and rewrite them."""

    check_connection()
    print("Connected to MongoDB.\n")

    validate()
    
    assets.delete_many({})
    edges.delete_many({})
    mitre.delete_many({})
    scenarios.delete_many({})
    print("Cleared existing documents.\n")

    assets.insert_many(ASSETS)
    edges.insert_many(EDGES)
    mitre.insert_many(MITRE_TECHNIQUES)
    scenarios.insert_many(SCENARIOS)

    print("Inserted:")
    print(f"  assets     : {assets.count_documents({})}")
    print(f"  edges      : {edges.count_documents({})}")
    print(f"  mitre      : {mitre.count_documents({})}")
    print(f"  scenarios  : {scenarios.count_documents({})}")
    print("\nSeeding complete.")


if __name__ == "__main__":
    run_seed()