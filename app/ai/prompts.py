def _summarise_context(result):
    scenario = result.get("scenario", {})
    risk = result.get("risk_score", 0)
    blast = result.get("blast_radius", {})
    impact = result.get("business_impact", {})
    critical = result.get("critical_assets", [])

    lines = [
        f"Scenario: {scenario.get('name', 'Unknown scenario')}",
        f"Attack type: {scenario.get('attack_type', 'unknown')}",
        f"Entry point: {result.get('start_asset_name', result.get('start_asset'))}",
        f"Risk score: {risk} out of 100",
        f"Systems reachable: {blast.get('assets_reachable', 0)} of {blast.get('total_assets', 0)} "
        f"({blast.get('percentage', 0)}% of the company)",
        f"Critical systems reachable: {len(critical)}",
        f"Records exposed: {impact.get('records_exposed', 0):,}",
        f"Business units affected: {impact.get('business_units_affected', 0)}",
    ]

    highest = impact.get("highest_value_asset")
    if highest:
        lines.append(
            f"Highest value system reached: {highest['name']} "
            f"({highest['record_count']:,} records, {highest['hops']} steps away)"
        )

    return "\n".join(lines)


def _format_path(attack_path):
    if not attack_path or not attack_path.get("steps"):
        return "No specific path available."

    lines = []

    for step in attack_path["steps"]:
        lines.append(
            f"{step['step']}. {step['from_name']} to {step['to_name']} "
            f"({step['relationship_type']}, {step['mitre_technique']}): {step['reason']}"
        )

    return "\n".join(lines)


def build_story_prompt(result, attack_path=None):
    return f"""You are a cybersecurity analyst writing an incident narrative.

Here are the facts of the incident:

{_summarise_context(result)}

How the attacker moved:
{_format_path(attack_path)}

Write a clear narrative of what happened, in 4 to 6 short paragraphs.

Rules:

- Write in past tense, as a sequence of events.
- Explain each step in plain English. If you must use a technical term, explain it in the same sentence.
- Use only the facts given above. Do not invent systems, numbers, dates or people.
- Do not use bullet points. Write flowing paragraphs.
- Do not add a heading or a title.
- End with what the attacker was ultimately able to access.
"""


def build_recommendations_prompt(result):
    critical = result.get("critical_assets", [])[:10]

    critical_lines = "\n".join(
        f"- {c['name']} ({c['business_unit']}, criticality {c['criticality']}, "
        f"{c['hops']} steps away, reached via {' then '.join(c['path'][-2:])})"
        for c in critical
    ) or "None reached."

    reachable = result.get("reachable", [])
    nearby = [r for r in reachable if r["hops"] == 1][:8]

    nearby_lines = "\n".join(
        f"- {r['name']}: {r['reached_via']['reason']}"
        for r in nearby
    ) or "None."

    return f"""You are a cybersecurity analyst recommending remediation actions.

Incident facts:

{_summarise_context(result)}

Critical systems the attacker can reach:
{critical_lines}

The first systems reached from the entry point, and why they were reachable:
{nearby_lines}

Produce between 5 and 7 recommended actions.

Rules:

- Order them by urgency, most urgent first.
- Each action must name a specific system from the lists above.
- Each action must be something a person could actually do this week.
- For each one, give the action in one sentence, then a second sentence explaining what it prevents.
- Prefer actions that cut off movement between systems over generic advice.
- Do not recommend anything generic such as "improve security awareness" unless it is tied to a specific system here.
- Return a numbered list only. No preamble, no closing paragraph.
"""


def build_executive_prompt(result):
    impact = result.get("business_impact", {})
    units = impact.get("affected_units", [])[:5]

    unit_lines = "\n".join(
        f"- {u['business_unit']}: {u['assets']} systems, {u['records']:,} records"
        for u in units
    ) or "None."

    return f"""You are writing for a company's executive leadership team. They are
intelligent but not technical, and they have two minutes.

Incident facts:

{_summarise_context(result)}

Business units affected:
{unit_lines}

Write exactly 4 sentences.

Rules:

- Sentence 1: what happened, in business terms.
- Sentence 2: what is at risk, using the records number and the business units.
- Sentence 3: how serious this is compared to a normal incident, using the risk score.
- Sentence 4: the single most important action to take now.
- Use no technical vocabulary. Do not use the words lateral, traversal, node, graph, endpoint, credential, token or hop.
- Do not use bullet points, headings or a title.
- Use only the numbers given above.
"""


def build_soc_prompt(result, attack_path=None, techniques=None):
    technique_lines = "None mapped."

    if techniques and techniques.get("techniques"):
        technique_lines = "\n".join(
            f"- {t['technique_id']} {t['name']} ({t['tactic']}), "
            f"observed on {t['occurrences']} transitions"
            for t in techniques["techniques"]
        )

    return f"""You are writing a summary for a security operations centre analyst.

They are technical and expect precise language.

Incident facts:

{_summarise_context(result)}

Attack path:
{_format_path(attack_path)}

MITRE ATT&CK techniques observed:
{technique_lines}

Write a technical summary in 3 short sections, using these exact headings:

Attack chain
Two or three sentences describing the progression, referencing MITRE technique
ids where relevant.

Detection opportunities
Three bullet points naming where in the chain this would have been detectable
and what signal to look for.

Containment priority
Two bullet points naming the specific transitions to break first and why.

Rules:

- Use the technique ids given above. Do not cite any technique not listed.
- Reference systems by their exact names.
- Be concise. This is a briefing, not an essay.
"""