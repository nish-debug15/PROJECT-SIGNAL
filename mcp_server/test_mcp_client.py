"""
MCP Client test — connects to the running SSE server and calls each tool.
Verifies the full MCP protocol loop (client → SSE → server → tool → response).

Prerequisites: MCP server running on port 8000
  uvicorn mcp_server.main:http_app --port 8000
"""
import asyncio
import json
import sys

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


async def main():
    print("Connecting to MCP server at http://localhost:8000/sse ...")

    async with sse_client("http://localhost:8000/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("Connected! Session initialized.\n")

            # List available tools
            tools_result = await session.list_tools()
            tool_names = [t.name for t in tools_result.tools]
            print(f"Available tools: {tool_names}\n")

            passed = 0
            failed = 0

            # Test 1: list_zones
            print("=" * 60)
            print("TEST 1: list_zones()")
            result = await session.call_tool("list_zones", {})
            data = json.loads(result.content[0].text)
            print(json.dumps(data, indent=2))
            assert data["count"] == 6, f"Expected 6 zones, got {data['count']}"
            print("[PASS]\n")
            passed += 1

            # Test 2: get_gtfs_routes — marathahalli
            print("=" * 60)
            print("TEST 2: get_gtfs_routes('marathahalli')")
            result = await session.call_tool("get_gtfs_routes", {"zone": "marathahalli"})
            data = json.loads(result.content[0].text)
            assert data["zone"] == "marathahalli"
            assert len(data["routes"]) == 4
            print(f"  Zone: {data['zone']}, Routes: {len(data['routes'])}, Adjacent: {data['adjacent_zones']}")
            print("[PASS]\n")
            passed += 1

            # Test 3: get_junction_signal_state — J-SB-01
            print("=" * 60)
            print("TEST 3: get_junction_signal_state('J-SB-01')")
            result = await session.call_tool("get_junction_signal_state", {"junction_id": "J-SB-01"})
            data = json.loads(result.content[0].text)
            assert data["junction_name"] == "Silk Board Junction"
            assert data["current_congestion"] == "critical"
            print(f"  Junction: {data['junction_name']}, Congestion: {data['current_congestion']}")
            print("[PASS]\n")
            passed += 1

            # Test 4: inject_incident
            print("=" * 60)
            print("TEST 4: inject_incident('marathahalli', 'accident', 'high')")
            result = await session.call_tool("inject_incident", {
                "location": "marathahalli",
                "incident_type": "accident",
                "severity": "high",
                "description": "MCP client test incident",
            })
            data = json.loads(result.content[0].text)
            assert data["status"] == "incident_created"
            inc = data["incident"]
            print(f"  Incident ID: {inc['incident_id']}")
            print(f"  Affected junctions: {inc['affected_junctions']}")
            print(f"  Affected routes: {inc['affected_routes']}")
            print("[PASS]\n")
            passed += 1

            # Test 5: get_active_incidents (should have the one we just created)
            print("=" * 60)
            print("TEST 5: get_active_incidents()")
            result = await session.call_tool("get_active_incidents", {})
            data = json.loads(result.content[0].text)
            assert data["count"] >= 1, f"Expected at least 1 incident, got {data['count']}"
            print(f"  Active incidents: {data['count']}")
            print("[PASS]\n")
            passed += 1

            print("=" * 60)
            print(f"RESULTS: {passed}/{passed+failed} MCP protocol tests passed")
            print("=" * 60)

            if failed > 0:
                sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
