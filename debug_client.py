import asyncio
import logging
import json
from fastmcp import Client
from fastmcp.client.auth import OAuth

logging.basicConfig(level=logging.INFO)


# ---------- AUTH ----------

class DebugOAuth(OAuth):
    async def redirect_handler(self, authorization_url: str):
        print("\n=== AUTHORIZE URL ===")
        print(authorization_url)
        print("=====================\n")

        input("Login in browser → press Enter...")

        return await super().redirect_handler(authorization_url)


oauth = DebugOAuth(
    scopes=["openid", "profile", "email", "groups", "approles"]
)

# ---------- CONTEXT (stores results for chaining) ----------

CONTEXT = {}


def store_result(key, result):
    if result.structured_content:
        content = result.structured_content
        if isinstance(content, dict) and "result" in content:
            CONTEXT[key] = content["result"]
        else:
            CONTEXT[key] = content


def get_first_id(key):
    items = CONTEXT.get(key, [])
    if not items:
        raise Exception(f"No data found for {key}")
    return items[0]["id"]


# ---------- TOOL EXECUTION ----------

async def run_tool(client, tool_name, payload=None):
    payload = payload or {}

    print(f"\n=== Running: {tool_name} ===")
    print("Input:", payload)

    result = await client.call_tool(tool_name, payload)

    print("\n=== STRUCTURED OUTPUT ===")
    if result.structured_content:
        print(json.dumps(result.structured_content, indent=2))
    else:
        print(result)

    return result


# ---------- FLOWS (SMART EXECUTION) ----------

async def health_check_flow(client):
    await run_tool(client, "health_check")

async def list_identity_collections_flow(client):
    res = await run_tool(client, "list_identity_collections")
    store_result("collections", res)

async def list_identities_flow(client):
    res = await run_tool(client, "list_identities")
    store_result("identities", res)

async def list_access_bundles_flow(client):
    await run_tool(client, "list_access_bundles")

async def list_orchestrated_systems_flow(client):
    await run_tool(client, "list_orchestrated_systems")

async def list_access_requests_flow(client):
    await run_tool(client, "list_access_requests")

async def create_identity_collection_flow(client):
    display_name = input("Collection Display Name: ")
    owner = input("Owner (email or name): ")
    included_raw = input("Included identities (comma separated, optional): ")

    included = [x.strip() for x in included_raw.split(",") if x.strip()]

    res = await run_tool(client, "create_identity_collection", {
        "display_name": display_name,
        "owner": owner,
        "included_identities": included
    })

async def create_access_request_flow(client):
    justification = input("Justification: ")

    created_by = input("Requester (name/email): ")

    beneficiaries_raw = input("Beneficiaries (comma separated): ")
    bundles_raw = input("Access Bundles (comma separated): ")

    beneficiaries = [x.strip() for x in beneficiaries_raw.split(",") if x.strip()]
    bundles = [x.strip() for x in bundles_raw.split(",") if x.strip()]

    await run_tool(client, "create_access_request", {
        "justification": justification,
        "created_by_user": created_by,
        "beneficiaries": beneficiaries,
        "access_bundles": bundles
    })

# ---------- MENU ----------

FLOWS = {
    "1": ("Health Check", health_check_flow),
    "2": ("List Identity Collections", list_identity_collections_flow),
    "3": ("List Identities", list_identities_flow),
    "4": ("Create Identity Collection", create_identity_collection_flow),
    "5": ("List Access Bundles", list_access_bundles_flow),
    "6": ("List Orchestrated Systems", list_orchestrated_systems_flow),
    "7": ("List Access Requests", list_access_requests_flow),
    "8": ("Create Access Request", create_access_request_flow)
}


# ---------- MAIN ----------

async def main():
    client = Client(
        "http://localhost:8000/mcp",
        auth=oauth
    )

    async with client:
        tools = await client.list_tools()

        print("\n=== AVAILABLE TOOLS ===")
        for t in tools:
            print("-", t.name)

        while True:
            print("\n=== ACTION MENU ===")
            for k, v in FLOWS.items():
                print(f"{k}. {v[0]}")
            print("0. Exit")

            choice = input("\nSelect action: ").strip()

            if choice == "0":
                print("Exiting...")
                break

            if choice not in FLOWS:
                print("Invalid choice")
                continue

            _, flow = FLOWS[choice]

            try:
                await flow(client)
            except Exception as e:
                print("\n❌ ERROR:", str(e))

if __name__ == "__main__":
    asyncio.run(main())