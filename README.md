# OCI Access Governance MCP Server

## Overview

The **OCI Access Governance MCP Server** exposes OCI Access Governance (AG) capabilities as MCP tools, enabling secure, programmatic interaction through MCP-compatible clients (e.g., Claude).

This server integrates with **OCI IAM (Identity Domains)** using OAuth 2.0 and enforces **authentication + role-based authorization** for all tool executions.

### Key Features

* OAuth 2.0 (OIDC) based authentication via OCI IAM
* Role-based access control using ID token claims
* MCP-compatible tool interface
* Async implementation using `aiohttp`
* Supports local development and packaged execution

---

## Architecture

1. User authenticates via OCI IAM (OIDC flow)
2. MCP server receives an ID token
3. Token is validated and roles are extracted
4. Access to tools is granted based on roles:

   * `AG_User`
   * `AG_Administrator`
5. Server uses client credentials flow to call OCI AG APIs

---

## Prerequisites

* Python 3.10+
* `uv` installed → https://github.com/astral-sh/uv
* OCI tenancy with:

  * Access Governance enabled
  * IAM Identity Domain configured

---

## Setup

### 1. Clone the repository

```
git clone https://github.com/anuj-git1412/oci-ag-mcp-server.git
cd oci-ag-mcp-server
```

---

### 2. Create environment configuration

```
cp .env.example .env
```

Update `.env` with your values:

```
# ---------- MCP Authentication (OIDC) ----------
OCI_CONFIG_URL=
OCI_MCP_CLIENT_ID=
OCI_MCP_CLIENT_SECRET=

# ---------- Access Governance API (Client Credentials) ----------
OCI_AG_CLIENT_ID=
OCI_AG_CLIENT_SECRET=
OCI_TOKEN_URL=
AG_BASE_URL=
AG_SCOPE=
```

---

## OAuth Configuration (OCI IAM)

Your OCI IAM OIDC application must include the following redirect URI:

```
http://localhost:8000/mcp/auth/callback
```

Authentication will fail if this does not match exactly.

---

## Running the Server

### Local Development

```
uvx --from . oracle.oci-ag-mcp-server
```

### Installed / Packaged Version

```
uvx oracle.oci-ag-mcp-server
```

---

### Server Endpoint

```
http://localhost:8000
```

---

## Available Tools

* `list_identities`
  Retrieve all identities (users)

* `list_identity_collections`
  Retrieve all identity collections (groups of users)

* `create_identity_collection`
  Create a new identity collection

* `list_access_bundles`
  Retrieve all access bundles

* `list_orchestrated_systems`
  Retrieve all orchestrated systems

* `list_access_requests`
  Retrieve all access requests

* `create_access_request`
  Create a new access request for users and access bundles

---

## Authentication & Authorization

* Users authenticate via OAuth (Authorization Code flow)
* ID token is validated by the server
* Roles are extracted from token claims
* Tool access is enforced based on roles

### Role Mapping

* `AG_User` → Read operations
* `AG_Administrator` → Full access (read + write)

---

## Project Structure

```
oracle/
  oci_ag_mcp_server/
    ag_client.py        # OCI AG API client
    auth.py             # OAuth / token handling
    server.py           # MCP server entrypoint
    consts.py           # Constants
    tests/              # Unit tests

examples/
  ag_mcp_test_client.py # Example MCP client
```

---

## Development Notes

* Uses async HTTP calls via `aiohttp`
* Token caching is implemented for AG API access
* Designed to be extended with additional AG operations
* MCP tools are defined and exposed via the server entrypoint

---

## Troubleshooting

**Authentication fails**

* Ensure redirect URI matches exactly
* Verify client ID and secret
* Check `OCI_CONFIG_URL`

**AG API calls fail**

* Verify `AG_BASE_URL` and `AG_SCOPE`
* Ensure client credentials are valid
* Check `OCI_TOKEN_URL`

**uvx not working**

* Ensure entrypoint exists in `pyproject.toml`
* Use `uvx --from .` for local runs

---

## License

Copyright (c) 2026 Oracle and/or its affiliates.

Licensed under the Universal Permissive License v1.0:
https://oss.oracle.com/licenses/upl/

