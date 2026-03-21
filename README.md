# OCI Access Governance MCP Server

## Overview

This server provides tools to interact with the OCI Access Governance (AG) service.

---

## Running the server

### STDIO transport mode

```bash
MCP_TRANSPORT=stdio uvx oracle.oci-ag-mcp-server
```

### HTTP streaming transport mode

```bash
MCP_TRANSPORT=http ORACLE_MCP_HOST=<hostname> ORACLE_MCP_PORT=<port> uvx oracle.oci-ag-mcp-server
```

---

## Environment Variables

The server supports the following environment variables:

### Access Governance API Authentication

* OCI_CLIENT_ID
* OCI_CLIENT_SECRET
* OCI_TOKEN_URL
* AG_SCOPE
* GRANT_TYPE

### MCP / Authentication

* OCI_MCP_CLIENT_ID
* OCI_MCP_CLIENT_SECRET
* OCI_CONFIG_URL
* MCP_SERVER_BASE_URL

### Service Endpoints

* AG_BASE_URL

---

## Tools

| Tool Name                  | Description                       |
| -------------------------- |-----------------------------------|
| list_identities            | Lists identities                  |
| list_identity_collections  | Lists identity collections        |
| create_identity_collection | Creates a new identity collection |
| list_access_bundles        | Lists access bundles              |
| list_orchestrated_systems  | Lists orchestrated systems        |
| list_access_requests       | Lists access requests             |
| create_access_request      | Creates a new access request      |

---

⚠️ NOTE: All actions are performed using configured OCI credentials. Use least-privilege IAM policies and secure credential handling.

---

## Third-Party APIs

Developers distributing this project are responsible for complying with licenses of any third-party dependencies.

---

## Disclaimer

Users are responsible for credential security and environment configuration.

---

## License

Copyright (c) 2026 Oracle and/or its affiliates.

Licensed under the Universal Permissive License v1.0:
https://oss.oracle.com/licenses/upl/
