"""
Copyright (c) 2026, Oracle and/or its affiliates.
Licensed under the Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl.
"""

from pydantic import BaseModel
from typing import Optional


# ----------- MODELS -----------

class Identity(BaseModel):
    id: str
    name: Optional[str]


class IdentityCollection(BaseModel):
    id: str
    name: str


class AccessBundle(BaseModel):
    id: str
    name: str

class OrchestratedSystem(BaseModel):
    id: str
    name: str
    type: Optional[str]


class AccessRequest(BaseModel):
    id: str
    justification: Optional[str]
    requestStatus: Optional[str]
    timeCreated: Optional[str]
    timeUpdated: Optional[str]


# ----------- MAPPERS -----------

def map_identity(raw: dict) -> Identity:
    return Identity(
        id=raw.get("id"),
        name=raw.get("name")
    )


def map_identity_collection(data: dict) -> IdentityCollection:
    name = (
            data.get("displayName")
            or data.get("name")
            or "Unknown"
    )

    return IdentityCollection(
        id=data.get("id"),
        name=name
    )


def map_access_bundle(raw: dict) -> AccessBundle:
    name = (
        raw.get("displayName")
        or raw.get("name")
        or "Unknown"
    )

    return AccessBundle(
        id=raw.get("id"),
        name=name
    )


def map_orchestrated_system(raw: dict) -> OrchestratedSystem:
    name = (
        raw.get("displayName")
        or raw.get("name")
        or "Unknown"
    )

    return OrchestratedSystem(
        id=raw.get("id"),
        name=name,
        type=raw.get("type")
    )


def map_access_request(raw: dict) -> AccessRequest:
    return AccessRequest(
        id=raw.get("id"),
        justification=raw.get("justification"),
        requestStatus=raw.get("requestStatus"),
        timeCreated=raw.get("timeCreated"),
        timeUpdated=raw.get("timeUpdated")
    )