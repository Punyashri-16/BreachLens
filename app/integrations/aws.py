def fetch_accounts():
    raise NotImplementedError


def fetch_iam_roles(account_id):
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
    raise NotImplementedError


def fetch_rds_instances(account_id):
    raise NotImplementedError


def fetch_secrets_metadata(account_id):
    raise NotImplementedError


def sync():
    raise NotImplementedError