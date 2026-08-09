SCENARIOS = [

    {
        "id": "SC001",
        "name": "Phishing Email Compromise",
        "description": (
            "An employee receives a message impersonating the Microsoft account team "
            "and enters their credentials on a fake login page. The attacker gains a "
            "foothold at the email gateway and moves toward the identity provider."
        ),
        "start_asset": "email_gateway",
        "attack_type": "phishing",
    },

    {
        "id": "SC002",
        "name": "Stolen Slack Session",
        "description": (
            "An attacker steals a session cookie from a compromised browser and takes "
            "over the employee's Slack account without needing the password or MFA. "
            "Credentials pasted in private channels become the next step."
        ),
        "start_asset": "slack",
        "attack_type": "session_hijack",
    },

    {
        "id": "SC003",
        "name": "Contractor Wiki Access",
        "description": (
            "A contractor account with read access to the internal wiki is compromised. "
            "Runbook pages containing connection strings and network keys turn a "
            "low-value account into a route toward internal systems."
        ),
        "start_asset": "confluence",
        "attack_type": "credential_theft",
    },

    {
        "id": "SC004",
        "name": "Developer Account Takeover",
        "description": (
            "An engineer's Jira account is compromised. Shared single sign-on carries "
            "the attacker into the code organisation, where a hardcoded deploy key "
            "opens the production cloud account."
        ),
        "start_asset": "jira",
        "attack_type": "account_takeover",
    },

    {
        "id": "SC005",
        "name": "Identity Provider Breach",
        "description": (
            "The single sign-on provider itself is compromised. This is the worst case "
            "for any modern organisation, because almost every business application "
            "trusts it to say who a user is."
        ),
        "start_asset": "okta",
        "attack_type": "identity_compromise",
    },

    {
        "id": "SC006",
        "name": "CI/CD Pipeline Compromise",
        "description": (
            "An attacker gains control of the build pipeline. The runner holds a "
            "production deployment role and push rights to the container registry, so "
            "malicious code reaches running infrastructure through trusted automation."
        ),
        "start_asset": "ci_runner",
        "attack_type": "supply_chain",
    },

    {
        "id": "SC007",
        "name": "Third-Party Tool Compromise",
        "description": (
            "The code scanning tool is breached at the vendor. It holds a long-lived "
            "access token for the code organisation, so a supplier incident becomes an "
            "internal one."
        ),
        "start_asset": "sonarqube",
        "attack_type": "third_party",
    },

    {
        "id": "SC008",
        "name": "Support Agent Compromise",
        "description": (
            "A support agent account is compromised. The support tool queries customer "
            "records directly through an API, so customer data is exposed in a single "
            "step without touching any infrastructure."
        ),
        "start_asset": "zendesk",
        "attack_type": "insider_access",
    },

    {
        "id": "SC009",
        "name": "Stolen Laptop on VPN",
        "description": (
            "An unlocked laptop with an active VPN profile is stolen. Internal-only "
            "business systems that rely on network location for protection become "
            "directly reachable."
        ),
        "start_asset": "vpn",
        "attack_type": "device_compromise",
    },

    {
        "id": "SC010",
        "name": "HR System Compromise",
        "description": (
            "The HR portal is compromised. Because it writes into the corporate "
            "directory to provision new joiners, an attacker can create accounts and "
            "escalate into identity infrastructure."
        ),
        "start_asset": "hr_portal",
        "attack_type": "privilege_escalation",
    },
]