"""
Lateral movement edges.

IMPORTANT: these are NOT attack paths. Each edge is a single fact about how
the company is configured or misconfigured. The attack paths are DISCOVERED
by running BFS over these facts. Nobody writes a path by hand.

weight = given the attacker controls `source`, how likely are they to obtain
         `target`. 0.9 is near-certain, 0.3 is a long shot.
mitre_technique = the ATT&CK technique that describes this movement.
"""

EDGES = [

    # ---------- PHISHING FOOTHOLD ----------
    # Email is where most real intrusions begin.
    {"source": "email_gateway", "target": "okta", "relationship_type": "credential_theft",
     "weight": 0.7, "mitre_technique": "T1566",
     "reason": "A phishing page harvests the employee's SSO credentials"},

    {"source": "email_gateway", "target": "slack", "relationship_type": "session_hijack",
     "weight": 0.6, "mitre_technique": "T1539",
     "reason": "The session cookie is stolen from the compromised browser"},

    # ---------- IDENTITY FANS OUT ----------
    # Whoever holds SSO holds most of the SaaS estate.
    {"source": "okta", "target": "slack", "relationship_type": "sso_access",
     "weight": 0.9, "mitre_technique": "T1078",
     "reason": "Slack authenticates through Okta SSO"},

    {"source": "okta", "target": "github_org", "relationship_type": "sso_access",
     "weight": 0.85, "mitre_technique": "T1078",
     "reason": "The GitHub organisation is federated to Okta"},

    {"source": "okta", "target": "google_drive", "relationship_type": "sso_access",
     "weight": 0.9, "mitre_technique": "T1078",
     "reason": "Google Workspace is federated to Okta"},

    {"source": "okta", "target": "salesforce", "relationship_type": "sso_access",
     "weight": 0.85, "mitre_technique": "T1078",
     "reason": "Salesforce authenticates through Okta SSO"},

    {"source": "okta", "target": "confluence", "relationship_type": "sso_access",
     "weight": 0.9, "mitre_technique": "T1078",
     "reason": "Confluence authenticates through Okta SSO"},

    {"source": "okta", "target": "vpn", "relationship_type": "sso_access",
     "weight": 0.8, "mitre_technique": "T1078",
     "reason": "VPN login is backed by the Okta directory"},

    {"source": "okta", "target": "zendesk", "relationship_type": "sso_access",
     "weight": 0.8, "mitre_technique": "T1078",
     "reason": "Zendesk authenticates through Okta SSO"},

    {"source": "active_directory", "target": "okta", "relationship_type": "directory_sync",
     "weight": 0.8, "mitre_technique": "T1078",
     "reason": "Okta syncs identities from Active Directory, so AD admin implies Okta control"},

    {"source": "mfa_service", "target": "okta", "relationship_type": "mfa_bypass",
     "weight": 0.6, "mitre_technique": "T1111",
     "reason": "Control of the MFA service allows enrolling an attacker-owned device"},

    # ---------- COLLABORATION LEAKS CREDENTIALS ----------
    # These systems are low value themselves and high value as stepping stones.
    {"source": "slack", "target": "confluence", "relationship_type": "credential_reuse",
     "weight": 0.5, "mitre_technique": "T1552",
     "reason": "The same SSO session token is accepted by Confluence"},

    {"source": "slack", "target": "aws_dev_account", "relationship_type": "hardcoded_credential",
     "weight": 0.45, "mitre_technique": "T1552",
     "reason": "Developers pasted temporary AWS keys into a private Slack channel"},

    {"source": "confluence", "target": "vpn", "relationship_type": "documented_credential",
     "weight": 0.55, "mitre_technique": "T1552",
     "reason": "A wiki runbook page contains the VPN pre-shared key"},

    {"source": "confluence", "target": "staging_db", "relationship_type": "documented_credential",
     "weight": 0.5, "mitre_technique": "T1552",
     "reason": "An onboarding page lists the staging database connection string"},

    {"source": "google_drive", "target": "payroll", "relationship_type": "documented_credential",
     "weight": 0.4, "mitre_technique": "T1552",
     "reason": "A finance spreadsheet contains payroll portal login details"},

    {"source": "jira", "target": "github_org", "relationship_type": "sso_access",
     "weight": 0.5, "mitre_technique": "T1078",
     "reason": "Jira and GitHub share the same identity provider session"},

    # ---------- CODE HOLDS SECRETS ----------
    # This is the mechanism that produces non-obvious reachability.
    {"source": "github_org", "target": "repo_payments", "relationship_type": "repo_access",
     "weight": 0.9, "mitre_technique": "T1213",
     "reason": "Organisation membership grants read access to the repository"},

    {"source": "github_org", "target": "repo_infra", "relationship_type": "repo_access",
     "weight": 0.85, "mitre_technique": "T1213",
     "reason": "Organisation membership grants read access to the repository"},

    {"source": "github_org", "target": "repo_frontend", "relationship_type": "repo_access",
     "weight": 0.9, "mitre_technique": "T1213",
     "reason": "Organisation membership grants read access to the repository"},

    {"source": "repo_payments", "target": "aws_prod_account", "relationship_type": "hardcoded_credential",
     "weight": 0.8, "mitre_technique": "T1552",
     "reason": "An AWS deploy key is hardcoded in the payments-api repository"},

    {"source": "repo_infra", "target": "vault", "relationship_type": "hardcoded_credential",
     "weight": 0.6, "mitre_technique": "T1552",
     "reason": "A Vault root token was committed to the infrastructure repository history"},

    {"source": "repo_frontend", "target": "cloudflare", "relationship_type": "hardcoded_credential",
     "weight": 0.5, "mitre_technique": "T1552",
     "reason": "A Cloudflare API token sits in the frontend deployment config"},

    {"source": "github_org", "target": "ci_runner", "relationship_type": "cicd_pivot",
     "weight": 0.75, "mitre_technique": "T1195",
     "reason": "Anyone who can push code can trigger the CI/CD pipeline"},

    {"source": "ci_runner", "target": "aws_prod_account", "relationship_type": "cicd_pivot",
     "weight": 0.8, "mitre_technique": "T1078",
     "reason": "The CI runner assumes the deploy-production IAM role"},

    {"source": "ci_runner", "target": "artifact_registry", "relationship_type": "cicd_pivot",
     "weight": 0.85, "mitre_technique": "T1195",
     "reason": "The pipeline holds push rights to the container registry"},

    {"source": "artifact_registry", "target": "eks_cluster", "relationship_type": "supply_chain",
     "weight": 0.7, "mitre_technique": "T1195",
     "reason": "A poisoned image is pulled and run by the Kubernetes cluster"},

    # ---------- CLOUD CONTROL PLANE ----------
    {"source": "vault", "target": "aws_prod_account", "relationship_type": "secret_access",
     "weight": 0.85, "mitre_technique": "T1552",
     "reason": "Vault issues dynamic AWS credentials for the production account"},

    {"source": "aws_iam", "target": "aws_prod_account", "relationship_type": "trust_relationship",
     "weight": 0.9, "mitre_technique": "T1078",
     "reason": "IAM policies grant administrative access to the production account"},

    {"source": "aws_dev_account", "target": "aws_prod_account", "relationship_type": "trust_relationship",
     "weight": 0.5, "mitre_technique": "T1548",
     "reason": "The development account is permitted to assume a role in production"},

    {"source": "aws_prod_account", "target": "s3_backups", "relationship_type": "cloud_access",
     "weight": 0.8, "mitre_technique": "T1530",
     "reason": "Backup buckets live inside this AWS account"},

    {"source": "aws_prod_account", "target": "s3_customer_exports", "relationship_type": "cloud_access",
     "weight": 0.8, "mitre_technique": "T1530",
     "reason": "Customer export buckets live inside this AWS account"},

    {"source": "aws_prod_account", "target": "production_db", "relationship_type": "cloud_access",
     "weight": 0.75, "mitre_technique": "T1078",
     "reason": "RDS production instances run inside this AWS account"},

    {"source": "aws_prod_account", "target": "eks_cluster", "relationship_type": "cloud_access",
     "weight": 0.8, "mitre_technique": "T1078",
     "reason": "The Kubernetes cluster runs on this AWS account"},

    {"source": "aws_prod_account", "target": "lambda_functions", "relationship_type": "cloud_access",
     "weight": 0.85, "mitre_technique": "T1078",
     "reason": "Lambda functions are deployed in this AWS account"},

    {"source": "aws_prod_account", "target": "s3_logs", "relationship_type": "cloud_access",
     "weight": 0.85, "mitre_technique": "T1530",
     "reason": "Log buckets live inside this AWS account and can be tampered with"},

    # ---------- REACHING THE DATA ----------
    {"source": "eks_cluster", "target": "production_db", "relationship_type": "credential_theft",
     "weight": 0.75, "mitre_technique": "T1552",
     "reason": "Database credentials are mounted as Kubernetes secrets in running pods"},

    {"source": "eks_cluster", "target": "redis_cache", "relationship_type": "network_access",
     "weight": 0.7, "mitre_technique": "T1210",
     "reason": "Redis is reachable without authentication from inside the cluster network"},

    {"source": "lambda_functions", "target": "payments_db", "relationship_type": "credential_theft",
     "weight": 0.65, "mitre_technique": "T1552",
     "reason": "Lambda environment variables contain the payments database password"},

    {"source": "production_db", "target": "customer_db", "relationship_type": "shared_service_account",
     "weight": 0.7, "mitre_technique": "T1078",
     "reason": "One service account has read access to both databases"},

    {"source": "s3_backups", "target": "customer_db", "relationship_type": "data_exposure",
     "weight": 0.65, "mitre_technique": "T1530",
     "reason": "Nightly backups contain a full copy of the customer database"},

    {"source": "redis_cache", "target": "customer_db", "relationship_type": "session_hijack",
     "weight": 0.5, "mitre_technique": "T1539",
     "reason": "Cached session tokens allow impersonating a customer-data application user"},

    {"source": "staging_db", "target": "customer_db", "relationship_type": "data_exposure",
     "weight": 0.45, "mitre_technique": "T1530",
     "reason": "Staging was refreshed from production without masking customer records"},

    {"source": "production_db", "target": "analytics_warehouse", "relationship_type": "data_pipeline",
     "weight": 0.6, "mitre_technique": "T1530",
     "reason": "A nightly ETL job replicates production tables into the warehouse"},

    {"source": "elasticsearch", "target": "customer_db", "relationship_type": "data_exposure",
     "weight": 0.4, "mitre_technique": "T1530",
     "reason": "Indexed documents mirror a large subset of customer records"},

    {"source": "eks_cluster", "target": "elasticsearch", "relationship_type": "network_access",
     "weight": 0.65, "mitre_technique": "T1210",
     "reason": "Elasticsearch is exposed inside the cluster network without authentication"},

    # ---------- BUSINESS SYSTEMS ----------
    {"source": "vpn", "target": "payroll", "relationship_type": "network_access",
     "weight": 0.6, "mitre_technique": "T1210",
     "reason": "Payroll is only reachable from the internal network, which the VPN provides"},

    {"source": "vpn", "target": "netsuite", "relationship_type": "network_access",
     "weight": 0.55, "mitre_technique": "T1210",
     "reason": "NetSuite restricts access to internal network ranges"},

    {"source": "payroll", "target": "hr_portal", "relationship_type": "shared_service_account",
     "weight": 0.65, "mitre_technique": "T1078",
     "reason": "Payroll and the HR portal share one integration service account"},

    {"source": "hr_portal", "target": "active_directory", "relationship_type": "provisioning_access",
     "weight": 0.5, "mitre_technique": "T1078",
     "reason": "The HR system writes into Active Directory to provision new joiners"},

    {"source": "salesforce", "target": "s3_customer_exports", "relationship_type": "data_pipeline",
     "weight": 0.6, "mitre_technique": "T1530",
     "reason": "Scheduled CRM exports are written to this bucket"},

    {"source": "zendesk", "target": "customer_db", "relationship_type": "api_access",
     "weight": 0.45, "mitre_technique": "T1213",
     "reason": "The support tool queries customer records through a read API"},

    {"source": "netsuite", "target": "payments_db", "relationship_type": "data_pipeline",
     "weight": 0.5, "mitre_technique": "T1530",
     "reason": "The ERP reconciles against payments data through a direct connection"},

    {"source": "docusign", "target": "google_drive", "relationship_type": "api_access",
     "weight": 0.4, "mitre_technique": "T1213",
     "reason": "Signed contracts are archived automatically to shared drives"},

    {"source": "google_drive", "target": "docusign", "relationship_type": "sso_access",
     "weight": 0.5, "mitre_technique": "T1078",
     "reason": "DocuSign authenticates using Google Workspace identity"},

    # ---------- MISC ----------
    {"source": "zoom", "target": "slack", "relationship_type": "credential_reuse",
     "weight": 0.3, "mitre_technique": "T1078",
     "reason": "Both use the same corporate identity, so one session hints at the other"},

    {"source": "sonarqube", "target": "github_org", "relationship_type": "api_access",
     "weight": 0.55, "mitre_technique": "T1213",
     "reason": "The code scanner holds a GitHub access token to read repositories"},

    {"source": "cloudflare", "target": "email_gateway", "relationship_type": "dns_hijack",
     "weight": 0.5, "mitre_technique": "T1584",
     "reason": "DNS control allows redirecting mail records to an attacker server"},
]