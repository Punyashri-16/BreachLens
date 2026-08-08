"""
Hits every endpoint through HTTP. Start uvicorn first, in another terminal.
Run with:  python -m app.test_routes
"""

import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def call(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except Exception as e:
        return 0, str(e)


def check(label, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}  {detail}")


print("\nTesting all routes\n")

s, d = call("GET", "/health")
check("GET /health", s == 200, d.get("database") if s == 200 else d)

s, d = call("GET", "/graph")
check("GET /graph", s == 200 and d["stats"]["total_nodes"] == 40,
      f"{d['stats']['total_nodes']} nodes" if s == 200 else d)

s, d = call("GET", "/scenarios")
check("GET /scenarios", s == 200,
      f"{len(d['scenarios'])} scenarios" if s == 200 else d)

s, incident = call("POST", "/simulate", {"scenario_id": "SC004"})
check("POST /simulate", s == 200,
      f"risk {incident['risk_score']}" if s == 200 else incident)

s, d = call("POST", "/counterfactual", {"scenario_id": "SC001", "limit": 3})
check("POST /counterfactual", s == 200,
      f"top drop {d['recommendations'][0]['percent_drop']} pct" if s == 200 else d)

if isinstance(incident, dict) and "risk_score" in incident:
    s, d = call("POST", "/story", {"incident": incident})
    check("POST /story", s == 200,
          f"{len(d.get('story',''))} chars" if s == 200 else d)

    s, d = call("POST", "/recommendations", {"incident": incident})
    check("POST /recommendations", s == 200,
          f"{d.get('count')} actions" if s == 200 else d)

    s, d = call("POST", "/bob", {
        "question": "Why is the customer database compromised?",
        "incident": incident,
    })
    check("POST /bob", s == 200, d.get("asset_id") if s == 200 else d)

print("\nBad input handling\n")

s, d = call("POST", "/simulate", {"scenario_id": "SC999"})
check("unknown scenario rejected", s == 0 and "404" in str(d), "")

print()