"""
Backend health check.

Run with:  python -m app.test_backend

Tests every layer bottom-up. If something fails, the layer it fails at
tells you where the problem is.
"""

from app.database.connection import assets, edges, mitre, scenarios, check_connection
from app.engine.graph_builder import build_graph
from app.engine.traversal import run_bfs, get_attack_path
from app.services.risk_service import assess
from app.services.mitre_service import summarise_techniques, map_path_to_techniques
from app.services.bob_service import ask_bob
import app.services.ai_service as ai

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {label}  {detail}")
    else:
        failed += 1
        print(f"  FAIL  {label}  {detail}")


print("\n" + "=" * 60)
print("1. DATABASE")
print("=" * 60)
try:
    check_connection()
    print("  PASS  MongoDB reachable")
    passed += 1
except Exception as e:
    print(f"  FAIL  MongoDB unreachable: {e}")
    print("\n  Start the MongoDB service and run this again.")
    raise SystemExit(1)

check("assets seeded", assets.count_documents({}) == 40, f"({assets.count_documents({})} expected 40)")
check("edges seeded", edges.count_documents({}) > 0, f"({edges.count_documents({})})")
check("mitre seeded", mitre.count_documents({}) > 0, f"({mitre.count_documents({})})")
check("scenarios seeded", scenarios.count_documents({}) > 0, f"({scenarios.count_documents({})})")


print("\n" + "=" * 60)
print("2. GRAPH")
print("=" * 60)
g = build_graph()
check("nodes loaded", g.number_of_nodes() == 40, f"({g.number_of_nodes()})")
check("edges loaded", g.number_of_edges() > 0, f"({g.number_of_edges()})")
check("no orphan nodes", all(g.degree(n) > 0 for n in g.nodes))
check("known asset present", "customer_db" in g)


print("\n" + "=" * 60)
print("3. TRAVERSAL")
print("=" * 60)
r = run_bfs(g, "jira")
check("bfs returns results", r["total_reached"] > 0, f"({r['total_reached']} assets)")
check("hops increase outward", r["reachable"][0]["hops"] == 1)
check("paths recorded", all(len(x["path"]) == x["hops"] + 1 for x in r["reachable"]))

bad = run_bfs(g, "does_not_exist")
check("bad start handled", bad["total_reached"] == 0 and "error" in bad)

p = get_attack_path(g, "jira", "customer_db")
check("attack path found", p is not None, f"({p['hops']} hops)" if p else "")
if p:
    check("path has labelled steps", all("mitre_technique" in s for s in p["steps"]))
    print("        route:", " -> ".join(p["path"]))


print("\n" + "=" * 60)
print("4. RISK SERVICE")
print("=" * 60)
risk = assess(g, r)
check("risk score in range", 0 <= risk["risk_score"] <= 100, f"({risk['risk_score']})")
check("blast radius computed", risk["blast_radius"]["assets_reachable"] > 0,
      f"({risk['blast_radius']['assets_reachable']}/{risk['blast_radius']['total_assets']})")
check("critical assets found", len(risk["critical_assets"]) > 0, f"({len(risk['critical_assets'])})")
check("records computed", risk["business_impact"]["records_exposed"] > 0,
      f"({risk['business_impact']['records_exposed']:,})")

# The engine must react to the input, not replay a script.
r2 = run_bfs(g, "zendesk")
risk2 = assess(g, r2)
check("different start gives different score",
      risk["risk_score"] != risk2["risk_score"],
      f"(jira {risk['risk_score']} vs zendesk {risk2['risk_score']})")


print("\n" + "=" * 60)
print("5. MITRE")
print("=" * 60)
t = summarise_techniques(r["reachable"])
check("techniques mapped", t["total_techniques"] > 0, f"({t['total_techniques']})")
check("no unknown techniques",
      all(x["name"] != "Unknown technique" for x in t["techniques"]))
if p:
    pt = map_path_to_techniques(p)
    check("path techniques mapped", len(pt) == len(p["steps"]))


print("\n" + "=" * 60)
print("6. AI LAYER (fallbacks must work with no API key)")
print("=" * 60)
incident = {**r, **risk}
ex = ai.generate_executive_summary(incident)
check("executive summary produced", len(ex) > 50, f"({len(ex)} chars)")
check("summary contains real numbers", str(risk["blast_radius"]["assets_reachable"]) in ex)

rec = ai.generate_recommendations(incident)
check("recommendations produced", len(rec) > 50)

b = ask_bob("Why is the customer database compromised?", incident)
check("bob answers", len(b["answer"]) > 30)
check("bob identified the asset", b["asset_id"] == "customer_db", f"({b['asset_id']})")


print("\n" + "=" * 60)
print(f"RESULT: {passed} passed, {failed} failed")
print("=" * 60 + "\n")

if failed == 0:
    print("Backend is working. Numbers for your demo:\n")
    print(f"  Jira scenario    : risk {risk['risk_score']}, "
          f"{risk['blast_radius']['assets_reachable']} systems, "
          f"{risk['business_impact']['records_exposed']:,} records")
    print(f"  Zendesk scenario : risk {risk2['risk_score']}, "
          f"{risk2['blast_radius']['assets_reachable']} systems, "
          f"{risk2['business_impact']['records_exposed']:,} records")
    print()