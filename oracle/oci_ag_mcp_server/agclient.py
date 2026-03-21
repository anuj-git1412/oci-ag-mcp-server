"""
Copyright (c) 2026, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl.
"""

import aiohttp
import os
from .consts import REQUEST_TIMEOUT, AG_API_VERSION
import time

class AGClient:

    def __init__(self):
        self.base_url = os.getenv("AG_BASE_URL")
        self.token_url = os.getenv("OCI_TOKEN_URL")
        self.client_id = os.getenv("OCI_CLIENT_ID")
        self.client_secret = os.getenv("OCI_CLIENT_SECRET")
        self.scope = os.getenv("AG_SCOPE")
        self._token = None
        self._token_expiry = 0

        # ---- validation ----
        required = {
            "AG_BASE_URL": self.base_url,
            "OCI_TOKEN_URL": self.token_url,
            "OCI_CLIENT_ID": self.client_id,
            "OCI_CLIENT_SECRET": self.client_secret,
            "AG_SCOPE": self.scope,
        }

        missing = [k for k, v in required.items() if not v]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    # -------- TOKEN --------

    async def _get_token(self):
        # Reuse token if still valid (add buffer of 30s)
        if self._token and time.time() < self._token_expiry - 30:
            return self._token

        async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.post(
                    self.token_url,
                    data={"grant_type": "client_credentials", "scope": self.scope},
                    auth=aiohttp.BasicAuth(self.client_id, self.client_secret)
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

                self._token = data["access_token"]

                # use expires_in if present, else default
                expires_in = data.get("expires_in", 3600)
                self._token_expiry = time.time() + expires_in

                return self._token

    # -------- GENERIC REQUEST --------

    async def _request(self, method, path, json=None):
        token = await self._get_token()

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        ) as session:
            async with session.request(
                method,
                f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {token}"},
                json=json
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    # -------- TOOL METHODS --------

    async def list_identities(self):
        return await self._request(
            "GET",
            f"/access-governance/identities/{AG_API_VERSION}/identities"
        )

    async def get_identity(self, identity_id):
        return await self._request(
            "GET",
            f"/access-governance/identities/{AG_API_VERSION}/identities/{identity_id}"
        )

    async def list_identity_collections(self):
        return await self._request(
            "GET",
            f"/access-governance/access-controls/{AG_API_VERSION}/identityCollections"
        )

    async def create_identity_collection(self, payload):
        return await self._request(
            "POST",
            f"/access-governance/access-controls/{AG_API_VERSION}/identityCollections",
            json=payload
        )

    async def list_access_reviews(self):
        return await self._request(
            "GET",
            f"/access-governance/access-reviews/{AG_API_VERSION}/accessReviews/identity"
        )

    async def get_access_review(self, review_id):
        return await self._request(
            "GET",
            f"/access-governance/access-reviews/{AG_API_VERSION}/accessReviews/{review_id}"
        )

    async def list_orchestrated_systems(self):
        return await self._request(
            "GET",
            f"/access-governance/service-administration/{AG_API_VERSION}/orchestratedSystems"
        )

    async def list_access_requests(self):
        return await self._request(
            "GET",
            f"/access-governance/access-controls/{AG_API_VERSION}/accessRequests"
        )

    async def list_access_bundles(self):
        return await self._request(
            "GET",
            f"/access-governance/access-controls/{AG_API_VERSION}/accessBundles"
        )

    async def create_access_request(self, payload: dict):
        return await self._request(
            "POST",
            f"/access-governance/access-controls/{AG_API_VERSION}/accessRequests",
            json=payload
        )