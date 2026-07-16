"""
Direct test script for MCP server tools.
Tests each tool function with synthetic data — no server needed.
"""
import json
import sys
sys.path.insert(0, ".")

from mcp_server.main import get_gtfs_routes, get_junction_signal_state, inject_incident, list_zones, list_junctions


def test_tool(name, result):
    print(f"\n{'='*60}")
    print(f"TOOL: {name}")
    print(f"{'='*60}")
    print(json.dumps(result, indent=2))
    if "error" in result:
        print(f"  ❌ RETURNED ERROR")
        return False
    print(f"  ✅ OK")
    return True


passed = 0
failed = 0

# Test 1: list_zones
r = list_zones()
if test_tool("list_zones()", r):
    passed += 1
else:
    failed += 1

# Test 2: list_junctions
r = list_junctions()
if test_tool("list_junctions()", r):
    passed += 1
else:
    failed += 1

# Test 3: get_gtfs_routes — valid zone
r = get_gtfs_routes("marathahalli")
if test_tool("get_gtfs_routes('marathahalli')", r):
    assert len(r["routes"]) > 0, "Expected routes"
    assert r["zone"] == "marathahalli"
    passed += 1
else:
    failed += 1

# Test 4: get_gtfs_routes — another zone
r = get_gtfs_routes("silk_board")
if test_tool("get_gtfs_routes('silk_board')", r):
    assert len(r["routes"]) > 0
    passed += 1
else:
    failed += 1

# Test 5: get_gtfs_routes — invalid zone
r = get_gtfs_routes("nonexistent_zone")
if "error" in r:
    print(f"\n{'='*60}")
    print(f"TOOL: get_gtfs_routes('nonexistent_zone') — expected error")
    print(f"{'='*60}")
    print(json.dumps(r, indent=2))
    print(f"  ✅ Correctly returned error for invalid zone")
    passed += 1
else:
    failed += 1

# Test 6: get_junction_signal_state — valid junction
r = get_junction_signal_state("J-MHL-01")
if test_tool("get_junction_signal_state('J-MHL-01')", r):
    assert r["junction_name"] == "Marathahalli Bridge Junction"
    assert len(r["phases"]) > 0
    passed += 1
else:
    failed += 1

# Test 7: get_junction_signal_state — Silk Board
r = get_junction_signal_state("J-SB-01")
if test_tool("get_junction_signal_state('J-SB-01')", r):
    assert r["current_congestion"] == "critical"
    passed += 1
else:
    failed += 1

# Test 8: inject_incident — valid
r = inject_incident(
    location="marathahalli",
    incident_type="accident",
    severity="high",
    description="Multi-vehicle pileup on ORR near Marathahalli Bridge",
)
if test_tool("inject_incident('marathahalli', 'accident', 'high')", r):
    assert r["status"] == "incident_created"
    assert len(r["incident"]["affected_junctions"]) > 0
    assert len(r["incident"]["affected_routes"]) > 0
    passed += 1
else:
    failed += 1

# Test 9: inject_incident — invalid type
r = inject_incident(location="marathahalli", incident_type="earthquake", severity="high")
if "error" in r:
    print(f"\n{'='*60}")
    print(f"TOOL: inject_incident(type='earthquake') — expected error")
    print(f"{'='*60}")
    print(json.dumps(r, indent=2))
    print(f"  ✅ Correctly rejected invalid incident type")
    passed += 1
else:
    failed += 1

# Test 10: inject_incident designed to trigger verifier rejection later
# (reroute into Silk Board which is already critical congestion)
r = inject_incident(
    location="koramangala",
    incident_type="waterlogging",
    severity="critical",
    description="Severe waterlogging at Koramangala. Traffic likely to be rerouted via Silk Board which is already at critical congestion.",
)
if test_tool("inject_incident('koramangala', 'waterlogging', 'critical') — future Block 4 test", r):
    passed += 1
else:
    failed += 1

print(f"\n{'='*60}")
print(f"RESULTS: {passed}/{passed+failed} tests passed")
print(f"{'='*60}")

if failed > 0:
    sys.exit(1)
