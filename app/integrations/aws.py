"""
AWS integration (not implemented).

This is where most of our critical assets and the trust relationships
between them would come from. AWS matters to the graph because it is
usually the point where an attacker converts access into reach: one
compromised role often exposes databases, buckets and compute at once.

Authentication: an IAM role assumed by our service with a read-only
policy. Specifically SecurityAudit and ViewOnlyAccess. No write
permissions anywhere.
"""


def fetch_accounts():
    """
    Fetch every account in the organisation.

    Would call organizations:ListAccounts. Each account becomes an asset
    of type "cloud", with criticality set from whether it is tagged as
    production.

    Writes into: assets
    """
    raise NotImplementedError


def fetch_iam_roles(account_id):
    """
    Fetch IAM roles and their attached policies.

    Would call iam:ListRoles and iam:ListAttachedRolePolicies. Roles
    holding administrative policies become high criticality assets.

    Writes into: assets
    """
    raise NotImplementedError


def fetch_assume_role_trusts(account_id):
    """
    Fetch cross-account trust relationships.

    Would read each role's AssumeRolePolicyDocument to find which
    principals may assume it. A development account permitted to assume
    a production role becomes an edge with relationship_type
    "trust_relationship" and mitre_technique T1548.

    These edges are how a low-value account becomes a path into
    production, and they are invisible to anyone reviewing permissions
    one account at a time.

    Writes into: edges
    """
    raise NotImplementedError


def fetch_s3_buckets(account_id):
    """
    Fetch buckets, their policies and their approximate object counts.

    Would call s3:ListBuckets and s3:GetBucketPolicy. Buckets tagged as
    holding customer data get their record_count populated from
    CloudWatch metrics, which is what feeds our business impact figure.

    Writes into: assets
    """
    raise NotImplementedError


def fetch_rds_instances(account_id):
    """
    Fetch database instances and the security groups around them.

    Would call rds:DescribeDBInstances. Each instance becomes a data
    asset, and its network reachability from compute resources becomes
    an edge with relationship_type "network_access".

    Writes into: assets, edges
    """
    raise NotImplementedError


def fetch_secrets_metadata(account_id):
    """
    Fetch secret names and which principals can read them.

    Would call secretsmanager:ListSecrets and read resource policies.
    We deliberately never fetch secret VALUES, only who can access them.
    A principal able to read a database secret becomes an edge to that
    database with mitre_technique T1552.

    Writes into: edges
    """
    raise NotImplementedError


def sync():
    """
    Run the full AWS synchronisation across all accounts.

    Returns counts of assets and edges written.
    """
    raise NotImplementedError