"""
Copyright (c) 2026, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl.
"""

import sys
import logging
import os

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# ---------------- ENV ----------------
from dotenv import load_dotenv
load_dotenv()

# ---------------- IMPORTS ----------------
from fastmcp import FastMCP
from pydantic import Field
from .auth import get_auth_provider, get_auth_middleware, require_roles_from_tags
from .agclient import AGClient
from .models import (
    map_identity,
    map_identity_collection,
    map_access_bundle,
    map_orchestrated_system,
    map_access_request
)

# ---------------- MCP INIT ----------------

mcp = FastMCP(
    name="oci-ag-mcp-server",
    auth=get_auth_provider(),
    middleware=[get_auth_middleware()]
)

client = AGClient()

# ---------------- TOOLS ----------------

@mcp.tool(
    name="health_check",
    description="Health check for MCP server"
)
async def health_check() -> dict:
    return {"status": "Healthy"}


@mcp.tool(
    name="list_identities",
    description="List identities in Access Governance"
)
async def list_identities() -> list[dict]:
    data = await client.list_identities()
    return [map_identity(d).model_dump() for d in data.get("items", [])]


@mcp.tool(
    name="list_identity_collections",
    description="List identity collections"
)
async def list_identity_collections() -> list[dict]:
    data = await client.list_identity_collections()
    return [map_identity_collection(d).model_dump() for d in data.get("items", [])]


@mcp.tool(
    name="create_identity_collection",
    description="Create a new identity collection",
    tags={"AG_Administrator"},
    auth=require_roles_from_tags
)
async def create_identity_collection(
    display_name: str = Field(...),
    owner: str = Field(...),
    included_identities: list[str] = Field(default_factory=list)
) -> dict:

    logger.info(f"Creating identity collection: {display_name}")

    owner_identity = await _resolve_identity(owner)

    included = []
    for x in included_identities:
        resolved = await _resolve_identity(x)
        included.append({
            "id": resolved["id"],
            "name": resolved["name"]
        })

    payload = {
        "name": _generate_name(display_name),
        "displayName": display_name,
        "description": _generate_description(display_name),
        "includedIdentities": included,
        "excludedIdentities": [],
        "owners": [
            {
                "id": owner_identity["id"],
                "name": owner_identity["name"],
                "isPrimary": True
            }
        ],
        "tags": _generate_tags(display_name),
        "isManagedAtOrchestratedSystem": False
    }

    return await client.create_identity_collection(payload)


@mcp.tool(
    name="list_access_bundles",
    description="List access bundles in Access Governance"
)
async def list_access_bundles() -> list[dict]:
    data = await client.list_access_bundles()
    return [map_access_bundle(d).model_dump() for d in data.get("items", [])]


@mcp.tool(
    name="list_orchestrated_systems",
    description="List orchestrated systems"
)
async def list_orchestrated_systems() -> list[dict]:
    data = await client.list_orchestrated_systems()
    return [map_orchestrated_system(d).model_dump() for d in data.get("items", [])]


@mcp.tool(
    name="list_access_requests",
    description="List access requests"
)
async def list_access_requests() -> list[dict]:
    data = await client.list_access_requests()
    return [map_access_request(d).model_dump() for d in data.get("items", [])]


@mcp.tool(
    name="create_access_request",
    description="Create a new access request",
    tags={"AG_User", "AG_Administrator"},
    auth=require_roles_from_tags
)
async def create_access_request(
    justification: str = Field(...),
    beneficiaries: list[str] = Field(...),
    access_bundles: list[str] = Field(...),
    created_by_user: str = Field(..., description="Requester name")
) -> dict:

    created_by = await _resolve_identity(created_by_user)

    identities = []
    for b in beneficiaries:
        resolved = await _resolve_identity(b)
        identities.append(resolved["id"])

    bundles = []
    for b in access_bundles:
        resolved = await _resolve_access_bundle(b)
        bundles.append(resolved["id"])

    payload = {
        "justification": justification,
        "createdBy": created_by["id"],
        "accessBundles": bundles,
        "identities": identities
    }

    logger.info("Creating access request")

    return await client.create_access_request(payload)


# ---------------- HELPERS ----------------

IDENTITY_CACHE = None
ACCESS_BUNDLE_CACHE = None


async def _get_identities():
    global IDENTITY_CACHE
    if IDENTITY_CACHE is None:
        data = await client.list_identities()
        IDENTITY_CACHE = [map_identity(d) for d in data.get("items", [])]
    return IDENTITY_CACHE


async def _resolve_identity(identifier: str) -> dict:
    identities = await _get_identities()
    identifier_lower = identifier.lower()

    for i in identities:
        if (
            identifier_lower == (i.id or "").lower()
            or identifier_lower == (i.name or "").lower()
        ):
            return {"id": i.id, "name": i.name}

    raise ValueError(f"Identity not found: {identifier}")


async def _get_access_bundles():
    global ACCESS_BUNDLE_CACHE
    if ACCESS_BUNDLE_CACHE is None:
        data = await client.list_access_bundles()
        ACCESS_BUNDLE_CACHE = [map_access_bundle(d) for d in data.get("items", [])]
    return ACCESS_BUNDLE_CACHE


async def _resolve_access_bundle(name: str) -> dict:
    bundles = await _get_access_bundles()
    name_lower = name.lower()

    for b in bundles:
        if (
            name_lower == (b.id or "").lower()
            or name_lower == (b.name or "").lower()
        ):
            return {"id": b.id, "name": b.name}

    raise ValueError(f"Access bundle not found: {name}")


def _generate_name(display_name: str) -> str:
    return display_name.lower().replace(" ", "_")


def _generate_description(display_name: str) -> str:
    return f"Identity collection for {display_name}"


def _generate_tags(display_name: str) -> list[str]:
    return [display_name.lower().replace(" ", "_")]


# ---------------- RUN ----------------

def main():
    transport = os.getenv("MCP_TRANSPORT", "http")

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(
            transport="http",
            host=os.getenv("ORACLE_MCP_HOST", "0.0.0.0"),
            port=int(os.getenv("ORACLE_MCP_PORT", "8000"))
        )


if __name__ == "__main__":
    main()