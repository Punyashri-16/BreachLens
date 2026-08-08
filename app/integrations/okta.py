"""
Okta integration (not implemented).

Okta is the top of the graph. Almost every application in a modern
company trusts it to say who a user is, which means a single compromised
identity fans out across the entire estate. Our seed file models this
with SSO edges; this module would build them from the real directory.

Authentication: an Okta API token with read-only administrator scope.

Note: Microsoft Entra ID would be a near-identical module against the
Graph API. We chose Okta as the reference implementation because the
concepts map one to one, so supporting both is a matter of adding a
second adapter rather than changing the engine.
"""


def fetch_users():
    """
    Fetch every active user in the directory.

    Would call GET /api/v1/users with a filter on active status. Each
    user becomes an identity in the graph, carrying their department and
    role, which is what lets us say a finance manager reached a
    production database.

    Writes into: assets, as identity type entries
    """
    raise NotImplementedError


def fetch_applications():
    """
    Fetch every application federated to Okta.

    Would call GET /api/v1/apps. Each application becomes an asset, and
    the fact that Okta authenticates it becomes an edge from Okta to
    that application with relationship_type "sso_access" and
    mitre_technique T1078.

    Writes into: assets, edges
    """
    raise NotImplementedError


def fetch_app_assignments(app_id):
    """
    Fetch which users and groups are assigned to an application.

    Would call GET /api/v1/apps/{appId}/users and /groups. These become
    the direct access edges from an identity to an asset, which are the
    starting points for every traversal.

    Writes into: edges
    """
    raise NotImplementedError


def fetch_groups():
    """
    Fetch groups and their memberships.

    Would call GET /api/v1/groups. Group membership is how access is
    granted in practice, so this is where over-provisioning shows up:
    someone left in a group long after changing role.

    Writes into: edges
    """
    raise NotImplementedError


def fetch_admin_roles():
    """
    Fetch users holding administrative roles in Okta itself.

    Would call GET /api/v1/users/{userId}/roles. An Okta administrator
    can grant themselves access to any federated application, so these
    identities receive edges to everything Okta controls.

    Writes into: edges
    """
    raise NotImplementedError


def sync():
    """
    Run the full Okta synchronisation.

    Returns counts of identities, applications and edges written.
    """
    raise NotImplementedError