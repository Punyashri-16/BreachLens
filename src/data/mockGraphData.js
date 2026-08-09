// 40 nodes and 58 edges topology representing corporate cloud infrastructure for BreachLens

export const MOCK_NODES = [
  { id: "email_gateway", name: "Email Security Gateway", type: "perimeter", criticality: 3, unit: "IT" },
  { id: "vpn_gateway", name: "VPN Gateway", type: "perimeter", criticality: 3, unit: "IT" },
  { id: "jira", name: "Jira Ticketing", type: "saas", criticality: 3, unit: "Engineering" },
  { id: "confluence", name: "Confluence Documentation", type: "saas", criticality: 3, unit: "Engineering" },
  { id: "slack", name: "Corporate Slack", type: "saas", criticality: 2, unit: "All" },
  { id: "okta", name: "Okta Identity Provider", type: "iam", criticality: 5, unit: "IT Security" },
  { id: "dev_workstation_1", name: "Sr. Dev Laptop (MacBook)", type: "endpoint", criticality: 3, unit: "Engineering" },
  { id: "dev_workstation_2", name: "DevOps Laptop (Ubuntu)", type: "endpoint", criticality: 4, unit: "DevOps" },
  { id: "support_workstation", name: "Support Rep Laptop", type: "endpoint", criticality: 2, unit: "Customer Care" },
  { id: "exec_workstation", name: "CFO Executive Laptop", type: "endpoint", criticality: 4, unit: "Finance" },
  { id: "github_org", name: "GitHub Organization", type: "scm", criticality: 4, unit: "Engineering" },
  { id: "repo_payments", name: "Payments Service Repo", type: "code", criticality: 4, unit: "FinTech Team" },
  { id: "repo_auth", name: "Auth Service Repo", type: "code", criticality: 4, unit: "Security Team" },
  { id: "repo_frontend", name: "Web Frontend Repo", type: "code", criticality: 2, unit: "Frontend Team" },
  { id: "ci_cd_pipeline", name: "GitHub Actions CI/CD", type: "devops", criticality: 4, unit: "DevOps" },
  { id: "docker_registry", name: "AWS ECR Container Registry", type: "devops", criticality: 3, unit: "DevOps" },
  { id: "bastion_host", name: "Production SSH Bastion", type: "compute", criticality: 4, unit: "DevOps" },
  { id: "aws_prod_account", name: "AWS Production Account", type: "cloud", criticality: 5, unit: "Infrastructure" },
  { id: "aws_staging_account", name: "AWS Staging Account", type: "cloud", criticality: 3, unit: "Infrastructure" },
  { id: "aws_iam_admin", name: "AWS Admin IAM Role", type: "iam", criticality: 5, unit: "Security" },
  { id: "k8s_prod_cluster", name: "EKS Production K8s", type: "compute", criticality: 5, unit: "Infrastructure" },
  { id: "payments_pod", name: "Payments API Service Pod", type: "compute", criticality: 4, unit: "Payments" },
  { id: "auth_pod", name: "Auth Microservice Pod", type: "compute", criticality: 4, unit: "Core Security" },
  { id: "api_gateway_prod", name: "Production API Gateway", type: "compute", criticality: 4, unit: "Infrastructure" },
  { id: "prod_db_master", name: "Production Customer DB", type: "database", criticality: 5, unit: "Data Engineering", record_count: 13303000 },
  { id: "prod_db_replica", name: "Customer DB Read Replica", type: "database", criticality: 4, unit: "Data Engineering", record_count: 13303000 },
  { id: "redis_cache", name: "Session Redis Cache", type: "database", criticality: 3, unit: "Infrastructure" },
  { id: "s3_customer_backups", name: "Customer DB Backup S3", type: "storage", criticality: 5, unit: "Data Engineering", record_count: 12000000 },
  { id: "s3_logs", name: "Production Audit Logs S3", type: "storage", criticality: 3, unit: "Security" },
  { id: "stripe_api_key", name: "Stripe Production API Secret", type: "secret", criticality: 5, unit: "Finance" },
  { id: "sendgrid_key", name: "SendGrid Email API Key", type: "secret", criticality: 2, unit: "Marketing" },
  { id: "snowflake_warehouse", name: "Snowflake Analytics DB", type: "database", criticality: 4, unit: "Analytics", record_count: 8500000 },
  { id: "zendesk", name: "Zendesk Support Desk", type: "saas", criticality: 2, unit: "Customer Care" },
  { id: "salesforce", name: "Salesforce CRM", type: "saas", criticality: 4, unit: "Sales", record_count: 2400000 },
  { id: "hr_portal", name: "Workday HR Platform", type: "saas", criticality: 3, unit: "HR" },
  { id: "legacy_ftp", name: "Internal Legacy FTP", type: "storage", criticality: 2, unit: "Operations" },
  { id: "ad_domain_controller", name: "Active Directory DC", type: "iam", criticality: 5, unit: "IT" },
  { id: "siem_splunk", name: "Splunk SIEM Log Collector", type: "monitoring", criticality: 3, unit: "Security" },
  { id: "vault_secrets", name: "HashiCorp Vault Master", type: "secret", criticality: 5, unit: "Security" },
  { id: "cloud_trail", name: "AWS CloudTrail Log Stream", type: "monitoring", criticality: 3, unit: "Security" }
];

export const MOCK_EDGES = [
  { source: "email_gateway", target: "dev_workstation_1", type: "phishing_email", reason: "Targeted spear-phishing email" },
  { source: "email_gateway", target: "dev_workstation_2", type: "phishing_email", reason: "Malicious attachment sent" },
  { source: "email_gateway", target: "support_workstation", type: "phishing_email", reason: "Support ticket phishing link" },
  { source: "email_gateway", target: "exec_workstation", type: "phishing_email", reason: "Executive credential harvesting" },
  { source: "dev_workstation_1", target: "okta", type: "stolen_session", reason: "Session cookie extracted from browser" },
  { source: "dev_workstation_1", target: "jira", type: "cached_credentials", reason: "Saved password in browser" },
  { source: "dev_workstation_1", target: "confluence", type: "sso_auth", reason: "Okta active session SSO" },
  { source: "dev_workstation_1", target: "github_org", type: "ssh_key", reason: "SSH key on developer machine" },
  { source: "dev_workstation_2", target: "aws_staging_account", type: "aws_profile", reason: "Stored AWS CLI credentials" },
  { source: "dev_workstation_2", target: "bastion_host", type: "ssh_key", reason: "Bastion SSH private key stored in ~/.ssh" },
  { source: "dev_workstation_2", target: "vault_secrets", type: "approle_token", reason: "Hardcoded Vault dev token" },
  { source: "support_workstation", target: "zendesk", type: "sso_auth", reason: "Active support agent login" },
  { source: "support_workstation", target: "salesforce", type: "sso_auth", reason: "Limited CRM access" },
  { source: "exec_workstation", target: "slack", type: "sso_auth", reason: "Exec session active" },
  { source: "exec_workstation", target: "hr_portal", type: "sso_auth", reason: "HR admin credentials" },
  { source: "okta", target: "jira", type: "sso_federation", reason: "Okta SAML 2.0 connection" },
  { source: "okta", target: "confluence", type: "sso_federation", reason: "Okta SAML 2.0 connection" },
  { source: "okta", target: "slack", type: "sso_federation", reason: "Okta SAML connection" },
  { source: "okta", target: "github_org", type: "sso_federation", reason: "Okta SAML 2.0 with SCIM provisioning" },
  { source: "okta", target: "aws_prod_account", type: "aws_sso", reason: "Okta AWS Identity Center integration" },
  { source: "jira", target: "github_org", type: "oauth_token", reason: "Leaked OAuth token in Jira ticket attachment" },
  { source: "confluence", target: "repo_payments", type: "hardcoded_credential", reason: "Plaintext database password in wiki page" },
  { source: "slack", target: "dev_workstation_2", type: "shared_secret", reason: "DevOps team channel credential dump" },
  { source: "github_org", target: "repo_payments", type: "repo_access", reason: "Developer team write permission" },
  { source: "github_org", target: "repo_auth", type: "repo_access", reason: "Developer team write permission" },
  { source: "github_org", target: "repo_frontend", type: "repo_access", reason: "Public internal repository" },
  { source: "repo_payments", target: "aws_prod_account", type: "hardcoded_credential", reason: "AWS deploy key hardcoded in CI workflow" },
  { source: "repo_payments", target: "stripe_api_key", type: "hardcoded_secret", reason: "Live Stripe secret key in config file" },
  { source: "repo_auth", target: "vault_secrets", type: "hardcoded_secret", reason: "Vault root token in test script" },
  { source: "repo_frontend", target: "sendgrid_key", type: "hardcoded_secret", reason: "SendGrid API key committed to frontend repo" },
  { source: "github_org", target: "ci_cd_pipeline", type: "webhook_trigger", reason: "Automated build pipeline execution" },
  { source: "ci_cd_pipeline", target: "docker_registry", type: "push_access", reason: "ECR push credentials in CI pipeline" },
  { source: "ci_cd_pipeline", target: "k8s_prod_cluster", type: "deploy_token", reason: "Kubeconfig secret stored in CI variables" },
  { source: "docker_registry", target: "k8s_prod_cluster", type: "image_pull", reason: "Kubernetes pod container deployment" },
  { source: "bastion_host", target: "aws_prod_account", type: "instance_profile", reason: "Bastion host EC2 IAM instance profile" },
  { source: "bastion_host", target: "k8s_prod_cluster", type: "network_peering", reason: "VPC Peering connection to EKS cluster" },
  { source: "aws_prod_account", target: "aws_iam_admin", type: "iam_role", reason: "Full AdministratorAccess IAM Role" },
  { source: "aws_prod_account", target: "k8s_prod_cluster", type: "aws_service", reason: "Managed EKS Cluster ownership" },
  { source: "aws_prod_account", target: "s3_customer_backups", type: "s3_bucket", reason: "Production S3 storage bucket" },
  { source: "aws_prod_account", target: "s3_logs", type: "s3_bucket", reason: "Audit logging S3 bucket" },
  { source: "aws_prod_account", target: "cloud_trail", type: "aws_service", reason: "CloudTrail logging stream" },
  { source: "aws_iam_admin", target: "prod_db_master", type: "admin_access", reason: "Full administrative access to RDS MySQL cluster" },
  { source: "aws_iam_admin", target: "snowflake_warehouse", type: "iam_trust", reason: "AWS IAM Role trust relationship with Snowflake" },
  { source: "k8s_prod_cluster", target: "payments_pod", type: "k8s_deployment", reason: "Running pod inside default namespace" },
  { source: "k8s_prod_cluster", target: "auth_pod", type: "k8s_deployment", reason: "Running pod inside auth namespace" },
  { source: "api_gateway_prod", target: "payments_pod", type: "ingress_routing", reason: "Public API route forwarding" },
  { source: "api_gateway_prod", target: "auth_pod", type: "ingress_routing", reason: "Public API route forwarding" },
  { source: "payments_pod", target: "prod_db_master", type: "db_connection", reason: "Direct JDBC database connection pool" },
  { source: "payments_pod", target: "redis_cache", type: "cache_connection", reason: "Redis cache TCP connection" },
  { source: "auth_pod", target: "prod_db_replica", type: "db_connection", reason: "Read replica connection" },
  { source: "auth_pod", target: "vault_secrets", type: "kv_lookup", reason: "Vault AppRole key-value retrieval" },
  { source: "prod_db_master", target: "prod_db_replica", type: "replication", reason: "MySQL binary log replication stream" },
  { source: "prod_db_master", target: "s3_customer_backups", type: "automated_backup", reason: "Nightly database snapshot upload" },
  { source: "prod_db_master", target: "snowflake_warehouse", type: "etl_pipeline", reason: "Fivetran automated ETL sync" },
  { source: "zendesk", target: "salesforce", type: "crm_integration", reason: "Customer profile sync" },
  { source: "ad_domain_controller", target: "legacy_ftp", type: "kerberos_auth", reason: "Active Directory domain join" },
  { source: "ad_domain_controller", target: "siem_splunk", type: "syslog_forward", reason: "Active Directory event log forwarding" },
  { source: "cloud_trail", target: "siem_splunk", type: "s3_ingestion", reason: "Splunk CloudTrail S3 log ingestion" }
];

export const MOCK_SCENARIOS = [
  { id: "SC001", name: "Email Gateway Phishing Campaign", description: "Attacker targets developers with spear-phishing emails containing malicious OAuth app authorization links.", start_asset: "email_gateway", attack_type: "phishing" },
  { id: "SC002", name: "VPN Credentials Leak", description: "Exposed corporate VPN credentials allow external connection into internal network.", start_asset: "vpn_gateway", attack_type: "credential_leak" },
  { id: "SC003", name: "Okta Session Hijacking", description: "Attacker intercepts Okta session cookie via session rider attack on unmanaged personal device.", start_asset: "okta", attack_type: "session_hijacking" },
  { id: "SC004", name: "Developer Account Takeover", description: "Compromised developer credentials grant access to Jira, GitHub, and embedded cloud keys.", start_asset: "jira", attack_type: "account_takeover" },
  { id: "SC005", name: "DevOps Laptop Malware", description: "DevOps engineer machine infected with info-stealer malware extracting SSH keys and AWS configs.", start_asset: "dev_workstation_2", attack_type: "endpoint_compromise" },
  { id: "SC006", name: "Confluence Hardcoded Credentials", description: "Anonymous read access to internal Wiki reveals database root credentials.", start_asset: "confluence", attack_type: "information_disclosure" },
  { id: "SC007", name: "CI/CD Pipeline Poisoning", description: "Compromised pull request modifies GitHub Actions workflow to extract EKS deploy secrets.", start_asset: "ci_cd_pipeline", attack_type: "supply_chain" },
  { id: "SC008", name: "Support Agent Credential Leak", description: "Support team member credentials compromised via password reuse on external site.", start_asset: "support_workstation", attack_type: "credential_leak" },
  { id: "SC009", name: "Legacy FTP Server Compromise", description: "Unpatched legacy FTP server exploited to breach Active Directory domain controller.", start_asset: "legacy_ftp", attack_type: "exploit_vulnerability" },
  { id: "SC010", name: "Public API Gateway Exploitation", description: "Broken object-level authorization (BOLA) in API gateway allows access to payments pod.", start_asset: "api_gateway_prod", attack_type: "api_abuse" }
];

export function getMockSimulateResult(scenarioId) {
  const scenario = MOCK_SCENARIOS.find(s => s.id === scenarioId) || MOCK_SCENARIOS[3];
  
  if (scenarioId === "SC008") {
    return {
      scenario,
      start_asset: "zendesk",
      start_asset_name: "Zendesk Support Desk",
      total_reached: 1,
      risk_score: 3.2,
      blast_radius: {
        assets_reachable: 1,
        total_assets: 39,
        percentage: 2.6,
        by_hop: { "1": 1 },
        max_hops: 1
      },
      business_impact: {
        records_exposed: 2400000,
        data_stores_reached: 1,
        business_units_affected: 1,
        affected_units: [
          { business_unit: "Customer Care", assets: 1, records: 2400000 }
        ],
        highest_value_asset: { asset_id: "salesforce", name: "Salesforce CRM", record_count: 2400000, hops: 1 }
      },
      critical_assets: [
        { asset_id: "salesforce", name: "Salesforce CRM", type: "saas", criticality: 4, business_unit: "Sales", record_count: 2400000, hops: 1, path: ["support_workstation", "zendesk", "salesforce"] }
      ],
      reachable: [
        {
          asset_id: "salesforce",
          name: "Salesforce CRM",
          type: "saas",
          criticality: 4,
          business_unit: "Sales",
          record_count: 2400000,
          hops: 1,
          path: ["zendesk", "salesforce"],
          reached_via: {
            from: "zendesk",
            relationship_type: "crm_integration",
            reason: "Customer profile sync token",
            mitre_technique: "T1078"
          }
        }
      ],
      mitre: {
        total_techniques: 2,
        techniques: [
          { technique_id: "T1078", name: "Valid Accounts", tactic: "Initial Access", description: "Use of compromised support accounts", occurrences: 1 }
        ],
        tactics: [{ tactic: "Initial Access", technique_count: 1 }]
      },
      headline_path: {
        path: ["support_workstation", "zendesk", "salesforce"],
        hops: 2,
        steps: [
          { step: 1, from: "support_workstation", from_name: "Support Rep Laptop", to: "zendesk", to_name: "Zendesk Support Desk", relationship_type: "sso_auth", weight: 1, reason: "Phished support agent SSO login", mitre_technique: "T1566" },
          { step: 2, from: "zendesk", from_name: "Zendesk Support Desk", to: "salesforce", to_name: "Salesforce CRM", relationship_type: "crm_integration", weight: 1, reason: "Zendesk to Salesforce auto-sync API key", mitre_technique: "T1078" }
        ]
      },
      incident_id: "INC-2026-SC008"
    };
  }

  // Default SC004 Developer Takeover response matching PDF specs:
  return {
    scenario,
    start_asset: "jira",
    start_asset_name: "Jira",
    total_reached: 35,
    risk_score: 30.8,
    blast_radius: {
      assets_reachable: 35,
      total_assets: 39,
      percentage: 89.7,
      by_hop: { "1": 4, "2": 9, "3": 12, "4": 6, "5": 4 },
      max_hops: 6
    },
    business_impact: {
      records_exposed: 13303000,
      data_stores_reached: 9,
      business_units_affected: 9,
      affected_units: [
        { business_unit: "Engineering", assets: 12, records: 5000000 },
        { business_unit: "Data Engineering", assets: 5, records: 13303000 }
      ],
      highest_value_asset: { asset_id: "prod_db_master", name: "Production Customer DB", record_count: 13303000, hops: 4 }
    },
    critical_assets: [
      { asset_id: "aws_prod_account", name: "AWS Production Account", type: "cloud", criticality: 5, business_unit: "Engineering", record_count: 0, hops: 3, path: ["jira", "github_org", "repo_payments", "aws_prod_account"] },
      { asset_id: "prod_db_master", name: "Production Customer DB", type: "database", criticality: 5, business_unit: "Data Engineering", record_count: 13303000, hops: 4, path: ["jira", "github_org", "repo_payments", "aws_prod_account", "prod_db_master"] }
    ],
    reachable: [
      {
        asset_id: "aws_prod_account",
        name: "AWS Production Account",
        type: "cloud",
        criticality: 5,
        business_unit: "Engineering",
        record_count: 0,
        hops: 3,
        path: ["jira", "github_org", "repo_payments", "aws_prod_account"],
        reached_via: {
          from: "repo_payments",
          relationship_type: "hardcoded_credential",
          reason: "An AWS deploy key is hardcoded in CI workflow script...",
          mitre_technique: "T1552"
        }
      }
    ],
    mitre: {
      total_techniques: 9,
      techniques: [
        { technique_id: "T1552", name: "Unsecured Credentials", tactic: "Credential Access", description: "Hardcoded AWS deploy key in repo", occurrences: 4 },
        { technique_id: "T1078", name: "Valid Accounts", tactic: "Defense Evasion", description: "Compromised developer account privileges", occurrences: 3 },
        { technique_id: "T1098", name: "Account Manipulation", tactic: "Persistence", description: "AWS Admin IAM role assumption", occurrences: 2 }
      ],
      tactics: [
        { tactic: "Credential Access", technique_count: 4 },
        { tactic: "Defense Evasion", technique_count: 3 },
        { tactic: "Persistence", technique_count: 2 }
      ]
    },
    headline_path: {
      path: ["jira", "github_org", "repo_payments", "aws_prod_account", "prod_db_master"],
      hops: 4,
      steps: [
        { step: 1, from: "jira", from_name: "Jira", to: "github_org", to_name: "GitHub Org", relationship_type: "oauth_token", weight: 1, reason: "Leaked OAuth token in Jira ticket attachment", mitre_technique: "T1552" },
        { step: 2, from: "github_org", from_name: "GitHub Org", to: "repo_payments", to_name: "Payments Service Repo", relationship_type: "repo_access", weight: 1, reason: "Developer has write access to repository", mitre_technique: "T1078" },
        { step: 3, from: "repo_payments", from_name: "Payments Service Repo", to: "aws_prod_account", to_name: "AWS Prod Account", relationship_type: "hardcoded_credential", weight: 1, reason: "AWS deploy key hardcoded in CI workflow", mitre_technique: "T1552" },
        { step: 4, from: "aws_prod_account", from_name: "AWS Prod Account", to: "prod_db_master", to_name: "Production Database", relationship_type: "admin_access", weight: 1, reason: "Full administrative IAM role to RDS cluster", mitre_technique: "T1098" }
      ]
    },
    incident_id: "INC-2026-SC004"
  };
}

export function getMockCounterfactualResult(scenarioId) {
  return {
    baseline_score: 43.5,
    baseline_assets_reachable: 34,
    baseline_critical_assets: 24,
    baseline_records_exposed: 13301800,
    edges_tested: 34,
    recommendations: [
      {
        source: "email_gateway",
        source_name: "Email Gateway",
        target: "okta",
        target_name: "Okta SSO",
        relationship_type: "credential_theft",
        reason: "A phishing page harvests developer credentials. Enforcing FIDO2 WebAuthn MFA eliminates phishing vector.",
        mitre_technique: "T1566",
        baseline_score: 43.5,
        new_score: 23.0,
        drop: 20.5,
        percent_drop: 47.1,
        assets_closed: 14,
        critical_assets_closed: 8,
        records_protected: 8500000,
        closed_asset_ids: ["aws_prod_account", "prod_db_master"],
        no_effect: false
      },
      {
        source: "github_org",
        source_name: "GitHub Org",
        target: "repo_payments",
        target_name: "Payments Service Repo",
        relationship_type: "hardcoded_credential",
        reason: "Enable GitHub Push Protection & Secret Scanning to block hardcoded AWS keys before commit.",
        mitre_technique: "T1552",
        baseline_score: 43.5,
        new_score: 28.2,
        drop: 15.3,
        percent_drop: 35.2,
        assets_closed: 9,
        critical_assets_closed: 5,
        records_protected: 4800000,
        closed_asset_ids: ["prod_db_master"],
        no_effect: false
      },
      {
        source: "aws_prod_account",
        source_name: "AWS Prod Account",
        target: "prod_db_master",
        target_name: "Production Database",
        relationship_type: "admin_access",
        reason: "Restrict RDS IAM Auth policies and require multi-party approval (JIT access) for database master access.",
        mitre_technique: "T1098",
        baseline_score: 43.5,
        new_score: 31.0,
        drop: 12.5,
        percent_drop: 28.7,
        assets_closed: 4,
        critical_assets_closed: 3,
        records_protected: 13303000,
        closed_asset_ids: ["prod_db_master", "prod_db_replica"],
        no_effect: false
      }
    ]
  };
}
