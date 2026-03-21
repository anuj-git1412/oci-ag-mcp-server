"""
Copyright (c) 2026, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl.
"""

import os
from fastmcp.server.auth.providers.oci import OCIProvider
from fastmcp.server.auth.oidc_proxy import OIDCProxy
from fastmcp.server.auth import AuthContext
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.exceptions import AuthorizationError

class CustomOCIProvider(OCIProvider):
    def __init__(self, **kwargs):
        OIDCProxy.__init__(self, verify_id_token=True, **kwargs)

def get_auth_provider():
    return CustomOCIProvider(
        config_url=os.getenv("OCI_CONFIG_URL"),
        client_id=os.getenv("OCI_MCP_CLIENT_ID"),
        client_secret=os.getenv("OCI_MCP_CLIENT_SECRET"),
        base_url=os.getenv("MCP_BASE_URL"),
        redirect_path=os.getenv("MCP_CALLBACK"),
        required_scopes=[
            "openid", "email", "groups", "approles","get_approles"
        ]
    )

def get_user_roles(ctx: AuthContext):
    token = ctx.token
    if token is None:
        raise AuthorizationError("Authentication required")

    roles = token.claims.get("appRoles", [])
    return {r.get("displayName") for r in roles if r.get("displayName")}


def require_ag_user(ctx: AuthContext):
    roles = get_user_roles(ctx)
    if not roles & {"AG_User", "AG_Administrator"}:
        raise AuthorizationError("Required roles missing")
    return True


def require_roles_from_tags(ctx: AuthContext):
    roles = get_user_roles(ctx)
    required_roles = ctx.component.tags

    if not required_roles.issubset(roles):
        raise AuthorizationError("Missing required role")

    return True


def get_auth_middleware():
    return AuthMiddleware(auth=require_ag_user)