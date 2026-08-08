from app.engine.graph_builder import build_graph
from app.engine.traversal import run_bfs, get_attack_path
from app.services.risk_service import assess
from app.services.mitre_service import summarise_techniques
import app.services.ai_service as ai

g = build_graph()
r = run_bfs(g, "jira")
result = {**r, **assess(g, r)}
path = get_attack_path(g, "jira", "customer_db")
techniques = summarise_techniques(r["reachable"])

print("=" * 60)
print("FALLBACKS ONLY — no API calls, no quota used")
print("=" * 60)

print("\n--- EXECUTIVE ---")
print(ai._fallback_executive(result))

print("\n--- RECOMMENDATIONS ---")
print(ai._fallback_recommendations(result))

print("\n--- STORY ---")
print(ai._fallback_story(result, path))

print("\n--- SOC ---")
print(ai._fallback_soc(result, path, techniques))

# Uncomment to try the real AI once your key works.
# print("\n--- LIVE AI EXECUTIVE ---")
# print(ai.generate_executive_summary(result))