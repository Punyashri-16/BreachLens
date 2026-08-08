"""
AI service.

Joins the prompt builders to the Gemini client. Each function takes a
simulation result, builds the right prompt, sends it, and returns text.

Every call passes a fallback built from the computed numbers, so a dead
API key, an exhausted quota or no network still produces a correct and
readable answer. The user never sees an error. This is what stops the
demo failing on stage.
"""

from app.ai.client import generate, is_available
from app.ai.prompts import (
    build_story_prompt,
    build_recommendations_prompt,
    build_executive_prompt,
    build_soc_prompt,
)


# ------------------------------------------------------------------
# FALLBACK BUILDERS
# These write plain text straight from the engine's numbers.
# No AI involved, so they always work and they are always accurate.
# ------------------------------------------------------------------

def _facts(result):
    """Pull the figures used by every fallback."""
    blast = result.get("blast_radius", {})
    impact = result.get("business_impact", {})
    return {
        "name": result.get("scenario", {}).get("name", "This incident"),
        "entry": result.get("start_asset_name", result.get("start_asset", "an entry point")),
        "score": result.get("risk_score", 0),
        "reached": blast.get("assets_reachable", 0),
        "total": blast.get("total_assets", 0),
        "pct": blast.get("percentage", 0),
        "critical": len(result.get("critical_assets", [])),
        "records": impact.get("records_exposed", 0),
        "units": impact.get("business_units_affected", 0),
        "top": impact.get("highest_value_asset"),
    }


def _fallback_story(result, attack_path):
    f = _facts(result)
    text = (
        f"{f['name']} began at {f['entry']}. From that single point of access, "
        f"an attacker was able to reach {f['reached']} of {f['total']} company "
        f"systems, which is {f['pct']} percent of the environment. "
        f"{f['critical']} of those systems are rated critical."
    )
    if attack_path and attack_path.get("steps"):
        steps = " Then ".join(
            f"{s['from_name']} led to {s['to_name']} because {s['reason'].lower()}"
            for s in attack_path["steps"]
        )
        text += f" The route taken was as follows. {steps}."
    text += (
        f" In total, approximately {f['records']:,} records across {f['units']} "
        f"business units were exposed."
    )
    return text


def _fallback_recommendations(result):
    lines = []
    for i, c in enumerate(result.get("critical_assets", [])[:6], start=1):
        via = c["path"][-2] if len(c["path"]) >= 2 else c["path"][0]
        lines.append(
            f"{i}. Break the connection from {via} to {c['name']}. "
            f"This system is rated criticality {c['criticality']} and sits "
            f"{c['hops']} steps from the entry point."
        )
    if not lines:
        lines.append("1. No critical systems were reachable in this scenario.")
    return "\n".join(lines)


def _fallback_executive(result):
    f = _facts(result)
    top = f["top"]
    top_text = (
        f" The most valuable system reached was {top['name']}, holding "
        f"{top['record_count']:,} records."
        if top else ""
    )
    return (
        f"{f['name']} started at {f['entry']} and spread to {f['reached']} of "
        f"{f['total']} company systems. Around {f['records']:,} records across "
        f"{f['units']} business units are at risk, including {f['critical']} "
        f"systems the business depends on.{top_text} This incident scores "
        f"{f['score']} out of 100 on our risk scale. The priority now is to cut "
        f"off access at the entry point and review the connections leading to "
        f"the highest value systems."
    )


def _fallback_soc(result, attack_path, techniques):
    f = _facts(result)
    parts = [
        "Attack chain",
        f"Entry at {f['entry']} expanded to {f['reached']} reachable assets "
        f"({f['pct']}% of the estate), including {f['critical']} critical systems.",
    ]
    if techniques and techniques.get("techniques"):
        ids = ", ".join(t["technique_id"] for t in techniques["techniques"][:6])
        parts.append(f"Techniques observed: {ids}.")
    parts.append("")
    parts.append("Containment priority")
    for c in result.get("critical_assets", [])[:3]:
        via = c["path"][-2] if len(c["path"]) >= 2 else c["path"][0]
        parts.append(f"- Sever {via} to {c['asset_id']} ({c['hops']} hops from entry).")
    return "\n".join(parts)


# ------------------------------------------------------------------
# PUBLIC FUNCTIONS
# These are what the routes call.
# ------------------------------------------------------------------

def generate_story(result, attack_path=None):
    """Narrative of what happened, for a general audience."""
    return generate(
        build_story_prompt(result, attack_path),
        temperature=0.4,
        fallback=_fallback_story(result, attack_path),
    )


def generate_recommendations(result):
    """Ranked remediation actions tied to specific systems."""
    return generate(
        build_recommendations_prompt(result),
        temperature=0.2,
        fallback=_fallback_recommendations(result),
    )


def generate_executive_summary(result):
    """Four sentences for leadership, no jargon."""
    return generate(
        build_executive_prompt(result),
        temperature=0.3,
        fallback=_fallback_executive(result),
    )


def generate_soc_summary(result, attack_path=None, techniques=None):
    """Technical briefing for a security analyst."""
    return generate(
        build_soc_prompt(result, attack_path, techniques),
        temperature=0.2,
        fallback=_fallback_soc(result, attack_path, techniques),
    )


def generate_all(result, attack_path=None, techniques=None):
    """
    All four at once. Used by the reporting endpoint.
    Note this makes four API calls, so avoid it on a tight quota.
    """
    return {
        "story": generate_story(result, attack_path),
        "recommendations": generate_recommendations(result),
        "executive_summary": generate_executive_summary(result),
        "soc_summary": generate_soc_summary(result, attack_path, techniques),
        "ai_used": is_available(),
    }