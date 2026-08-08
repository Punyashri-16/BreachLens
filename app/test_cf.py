from app.engine.graph_builder import build_graph
from app.services.counterfactual_service import analyse_counterfactuals

graph = build_graph()

for start in ["email_gateway", "jira"]:
    r = analyse_counterfactuals(graph, start, limit=5)
    print()
    print("=" * 70)
    print(f"{r['start_asset_name']}  |  baseline score {r['baseline_score']}"
          f"  |  reaches {r['baseline_assets_reachable']} assets"
          f"  |  {r['edges_tested']} edges tested")
    print("=" * 70)

    for x in r["recommendations"]:
        print(f"\n  Cut  {x['source']} -> {x['target']}")
        print(f"       score {x['baseline_score']} -> {x['new_score']}"
              f"   drop {x['percent_drop']} percent")
        print(f"       closes {x['assets_closed']} assets,"
              f" {x['critical_assets_closed']} critical")
        print(f"       {x['reason']}")
        if x["no_effect"]:
            print("       NO EFFECT - another route already exists")
    print()