MITRE_TECHNIQUES = [

    {
        "technique_id": "T1566",
        "name": "Phishing",
        "tactic": "Initial Access",
        "description": "An attacker sends a deceptive message to trick a user into revealing credentials or running malicious content.",
    },
    {
        "technique_id": "T1584",
        "name": "Compromise Infrastructure",
        "tactic": "Resource Development",
        "description": "An attacker takes control of infrastructure such as DNS records to redirect or intercept legitimate traffic.",
    },

    {
        "technique_id": "T1552",
        "name": "Unsecured Credentials",
        "tactic": "Credential Access",
        "description": "Credentials are found in source code, configuration files, environment variables or documentation rather than a secret store.",
    },
    {
        "technique_id": "T1539",
        "name": "Steal Web Session Cookie",
        "tactic": "Credential Access",
        "description": "A valid session cookie is stolen and replayed, allowing access without knowing the password or passing MFA.",
    },
    {
        "technique_id": "T1111",
        "name": "Multi-Factor Authentication Interception",
        "tactic": "Credential Access",
        "description": "An attacker bypasses MFA by intercepting codes or enrolling a device they control.",
    },
    {
        "technique_id": "T1110",
        "name": "Brute Force",
        "tactic": "Credential Access",
        "description": "An attacker repeatedly guesses passwords or reuses credentials leaked from other breaches.",
    },

    {
        "technique_id": "T1078",
        "name": "Valid Accounts",
        "tactic": "Defense Evasion, Persistence, Privilege Escalation, Initial Access",
        "description": "An attacker uses legitimate credentials to access systems, which makes their activity difficult to distinguish from normal use.",
    },
    {
        "technique_id": "T1210",
        "name": "Exploitation of Remote Services",
        "tactic": "Lateral Movement",
        "description": "An attacker reaches an internal service that is exposed on the network without adequate authentication.",
    },
    {
        "technique_id": "T1548",
        "name": "Abuse Elevation Control Mechanism",
        "tactic": "Privilege Escalation",
        "description": "An attacker assumes a more privileged role or trust relationship to gain higher access.",
    },
    {
        "technique_id": "T1550",
        "name": "Use Alternate Authentication Material",
        "tactic": "Lateral Movement",
        "description": "An attacker moves between systems using tokens, keys or hashes instead of a password.",
    },

    {
        "technique_id": "T1213",
        "name": "Data from Information Repositories",
        "tactic": "Collection",
        "description": "An attacker mines wikis, ticketing systems and code repositories for sensitive information.",
    },
    {
        "technique_id": "T1087",
        "name": "Account Discovery",
        "tactic": "Discovery",
        "description": "An attacker enumerates user accounts and groups to identify which identities are worth targeting next.",
    },

    {
        "technique_id": "T1195",
        "name": "Supply Chain Compromise",
        "tactic": "Initial Access",
        "description": "An attacker inserts malicious code into the build pipeline or a dependency so it is deployed by trusted automation.",
    },

    {
        "technique_id": "T1530",
        "name": "Data from Cloud Storage Object",
        "tactic": "Collection",
        "description": "An attacker reads data directly from cloud storage buckets, databases or backups.",
    },
    {
        "technique_id": "T1567",
        "name": "Exfiltration Over Web Service",
        "tactic": "Exfiltration",
        "description": "Stolen data is sent out through a legitimate web service so the traffic blends in with normal activity.",
    },
    {
        "technique_id": "T1486",
        "name": "Data Encrypted for Impact",
        "tactic": "Impact",
        "description": "An attacker encrypts data to disrupt the business and demand payment for its recovery.",
    },
]