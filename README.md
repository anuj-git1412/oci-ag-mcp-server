# OCI Access Governance MCP Server

## Overview

This server provides tools to interact with the OCI Access Governance (AG) service.

It uses OAuth 2.0 for authentication and authorization via an OCI IAM Domain:

- The MCP server integrates with an OCI IAM OIDC application
- Users authenticate through the OAuth authorization flow
- An ID token is issued and attached to requests
- Tool access is controlled based on roles present in the token (e.g., AG_User, AG_Administrator)

All tool executions are protected by authentication and role-based authorization.

---

## Setup

### 1. Create environment configuration

Copy the example file:

cp .env.example .env

Update .env with your values:

OCI_CONFIG_URL=

OCI_MCP_CLIENT_ID=

OCI_MCP_CLIENT_SECRET=

OCI_AG_CLIENT_ID=

OCI_AG_CLIENT_SECRET=

OCI_TOKEN_URL=

AG_BASE_URL=

AG_SCOPE=

---

## OAuth Configuration

Your OCI IAM application must include the following redirect URI:

http://localhost:8000/mcp/auth/callback

Authentication will fail if this does not match exactly.

---

## Running the Server

uvx oracle.oci-ag-mcp-server

Runs on: http://localhost:8000

---

## Tools

| Tool Name                  | Description                                                      |
|--------------------------|------------------------------------------------------------------|
| list_identities           | Retrieve all identities (users)                                  |
| list_identity_collections | Retrieve all identity collections (groups of users)              |
| create_identity_collection| Create a new identity collection                                 |
| list_access_bundles       | Retrieve all access bundles                                      |
| list_orchestrated_systems | Retrieve all orchestrated systems                                |
| list_access_requests      | Retrieve all access requests                                     |
| create_access_request     | Create a new access request for users and access bundles         |

---

## License

Copyright (c) 2026 Oracle and/or its affiliates.

Licensed under the Universal Permissive License v1.0:
https://oss.oracle.com/licenses/upl/