# Oracle Access Governance MCP Server

## Overview

The Oracle Access Governance MCP Server exposes Access Governance (AG) capabilities as MCP tools, enabling secure interaction from MCP-compatible clients (e.g., Claude, custom clients etc.).

It integrates with OCI IAM (Identity Domains) using OAuth 2.0 (OIDC) to authenticate MCP clients.

### Flow
1. A client (user or agent) sends a request to the MCP server
2. If unauthenticated, the request is redirected via OIDC/OAuth proxy to OCI IAM
3. The user authenticates with OCI IAM
4. OCI IAM issues tokens, which are validated by the proxy/MCP layer
5. MCP server establishes its own session or issues an MCP-specific token
6. Client uses MCP-issued session/token for subsequent requests

---

## Setup

### 1. Clone the repository

```
git clone https://github.com/anuj-git1412/oci-ag-mcp-server.git
cd oci-ag-mcp-server
```

### 2. Configure OAuth (OCI IAM)

Setting up authentication requires registering a confidential client application in OCI IAM domain.
Make sure to select "Authorization code" and "Client credentials" under Allowed grant types.
The application must also include the following redirect URI:

```
http://localhost:8000/mcp/auth/callback
```

Register a second confidential application to access AG APIs.
Ensure that the application is assigned the appropriate AG scope.

---

### 3. Create environment configuration

Create a `.env` file and populate it with your configuration values:

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

## Running the Server

### Set the environment:

```
export $(cat .env | xargs)
```

### Run the server:

```
uvx oracle.oci-ag-mcp-server
```

---

## Available Tools

| Tool Name                    | Description                                                                  |
|------------------------------|------------------------------------------------------------------------------|
| `list_identities`            | Retrieve all identities (users) from the AG environment.                     |
| `list_identity_collections`  | Retrieve all identity collections (groups of users) from the AG environment. |
| `create_identity_collection` | Creates a new identity collection in the AG environment.                     |
| `list_access_bundles`        | Retrieve all access bundles from the AG environment.                         |
| `list_orchestrated_systems`  | Retrieve all orchestrated systems from the AG environment.                   |
| `list_access_requests`       | Retrieve all access requests from the AG environment.                        |
| `create_access_request`      | Creates a new access request in the AG environment.                          |
| `health_check`               | Returns basic health status.                                                 |
---

## License

Copyright (c) 2026 Oracle and/or its affiliates.

Licensed under the Universal Permissive License v1.0:
https://oss.oracle.com/licenses/upl/

