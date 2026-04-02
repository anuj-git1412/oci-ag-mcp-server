"""
Copyright (c) 2026, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl.
"""
import logging
import os

from fastmcp.server.auth import OIDCProxy
from fastmcp.server.auth import AuthContext
from fastmcp.server.middleware import AuthMiddleware
from fastmcp.exceptions import AuthorizationError

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,  # change to INFO in prod
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

# ---------- AUTH PROVIDER ----------

class MyOCIProvider(OIDCProxy):

    def _prepare_scopes_for_token_exchange(self, scopes: list[str]) -> list[str]:
        return []

def get_auth_provider_new():

    return MyOCIProvider(
        config_url=os.getenv("OCI_CONFIG_URL"),
        client_id=os.getenv("OCI_MCP_CLIENT_ID"),
        client_secret=os.getenv("OCI_MCP_CLIENT_SECRET"),
        base_url="https://mcp.anuj.online",
        redirect_path="/mcp/auth/callback",
        required_scopes=["openid", "get_approles", "approles"],
        verify_id_token=True
    )

def get_user_roles(ctx: AuthContext):
    token = ctx.token
    if token is None:
        raise AuthorizationError("Authentication required")

    roles = token.claims.get("appRoles", [])
    return {r.get("displayName") for r in roles if r.get("displayName")}


def require_ag_user(ctx: AuthContext):
    logger.info("Middleware auth begin")
    roles = get_user_roles(ctx)
    required_roles_mw = {"AG_User", "AG_Administrator"}
    logger.info("User roles extracted from token: %s", roles)
    if not roles & required_roles_mw:

        logger.error(
            "Authorization failed at middleware level: User lacks required roles."
            " Required=AG_User OR AG_Administrator, Found=%s",
            roles)
        raise AuthorizationError("Required roles missing at middleware layer")

    logger.info("Authorization passed at middleware level")
    logger.info("Middleware auth end")
    return True


def require_roles_from_tags(ctx: AuthContext):
    logger.info("Tool level auth begin")
    roles = get_user_roles(ctx)
    required_roles = ctx.component.tags

    logger.info("User roles extracted from token: %s", roles)

    if "AG_Administrator" in roles:
        logger.info("User is an AG Administrator")
        logger.info("Authorization passed at tool level")
        return True

    if not required_roles.issubset(roles):
        logger.error(
            "Authorization failed: user lacks required roles. Required=%s, Found=%s",
            required_roles, roles)
        raise AuthorizationError("Required roles missing at tool level")

    logger.info("Authorization passed at tool level")
    logger.info("Tool level auth end")
    return True


def get_auth_middleware():
    return AuthMiddleware(auth=require_ag_user)