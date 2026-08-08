"""
GitHub integration (not implemented).

In production this replaces the hand-written repository entries in our
seed file. GitHub is important to us for one reason: repositories leak
credentials, and a leaked key turns a low-value account into a route
into cloud infrastructure. Our graph already models that as an edge;
this module would discover those edges automatically instead.

Authentication: a GitHub App installation token, read-only, scoped to
the organisation. Never a personal access token.
"""


def fetch_repositories(org):
    """
    Fetch every repository in the organisation.

    Would call GET /orgs/{org}/repos and return a list of dictionaries
    shaped like our Asset model, with type set to "code" and criticality
    derived from whether the repository deploys to production.

    Writes into: assets
    """
    raise NotImplementedError


def fetch_repository_collaborators(org, repo):
    """
    Fetch who can read each repository.

    Would call GET /repos/{org}/{repo}/collaborators. This is the data
    that reveals over-provisioning, where someone outside engineering
    still has read access to a repository months after they needed it.

    Writes into: edges, as identity to asset relationships
    """
    raise NotImplementedError


def scan_repository_secrets(org, repo):
    """
    Find credentials committed into a repository.

    Would call GET /repos/{org}/{repo}/secret-scanning/alerts, which
    reports detected keys including AWS credentials.

    Each alert becomes a lateral movement edge from the repository to
    whatever the credential unlocks, with relationship_type set to
    "hardcoded_credential" and mitre_technique T1552. This is the single
    highest value call in this module, because these edges are the ones
    no permission review would ever surface.

    Writes into: edges
    """
    raise NotImplementedError


def fetch_actions_workflows(org, repo):
    """
    Fetch CI/CD workflow definitions and the roles they assume.

    Would call GET /repos/{org}/{repo}/actions/workflows and inspect the
    OIDC role bindings. A workflow that assumes a production deployment
    role becomes an edge from the runner to that cloud account, with
    relationship_type "cicd_pivot".

    Writes into: edges
    """
    raise NotImplementedError


def sync(org):
    """
    Run the full GitHub synchronisation.

    Calls the functions above in order, upserts the results, and returns
    counts of assets and edges written. Intended to run on a schedule so
    the graph reflects the current state rather than a point in time.
    """
    raise NotImplementedError