"""
SIGNAL MCP Server — Main entry point.

FastMCP server exposing three tools for the SIGNAL agent system:
  - get_gtfs_routes(zone)
  - get_junction_signal_state(junction_id)
  - inject_incident(location, type, severity)

Run: python -m mcp_server.main  (stdio mode for ADK)
  or: uvicorn mcp_server.main:http_app --port 8000  (HTTP/SSE mode for curl testing)
"""

import uuid
import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from mcp_server.data.synthetic import (
    get_zone,
    get_junction,
    get_junctions_in_zone,
    list_all_zones,
    list_all_junctions,
    Incident,
)


# --- MCP Server ---

mcp = FastMCP(
    "signal-traffic-server",
    instructions=(
        "SIGNAL Traffic Data Server. Provides Bengaluru BMTC route data, "
        "junction signal states, and incident injection for the SIGNAL "
        "multi-agent traffic response system."
    ),
)


# In-memory incident store (reset on server restart)
_active_incidents: dict[str, Incident] = {}


@mcp.tool()
def get_gtfs_routes(zone: str) -> dict[str, Any]:
    """Get BMTC bus routes operating in the specified zone.

    Args:
        zone: Name of the Bengaluru zone (e.g. 'marathahalli', 'silk_board',
              'kr_puram', 'koramangala', 'whitefield', 'indiranagar').

    Returns:
        Dict with zone info including routes, coordinates, and adjacent zones.
        Returns error dict if zone not found.
    """
    zone_data = get_zone(zone)
    if zone_data is None:
        available = list_all_zones()
        return {
            "error": f"Zone '{zone}' not found.",
            "available_zones": available,
        }
    return zone_data.model_dump()


@mcp.tool()
def get_junction_signal_state(junction_id: str) -> dict[str, Any]:
    """Get current signal timing and congestion state for a junction.

    Args:
        junction_id: Junction ID (e.g. 'J-MHL-01', 'J-SB-01') or junction name
                     (e.g. 'Silk Board Junction'). Case-insensitive.

    Returns:
        Dict with junction info including signal phases, cycle time, and
        current congestion level. Returns error dict if junction not found.
    """
    junction = get_junction(junction_id)
    if junction is None:
        available = list_all_junctions()
        return {
            "error": f"Junction '{junction_id}' not found.",
            "available_junctions": available,
        }
    return junction.model_dump()


@mcp.tool()
def inject_incident(
    location: str,
    incident_type: str,
    severity: str,
    description: str = "",
) -> dict[str, Any]:
    """Inject a synthetic traffic incident for the SIGNAL system to respond to.

    Args:
        location: Location name or zone (e.g. 'Marathahalli Bridge', 'Silk Board').
                  Must match a known zone.
        incident_type: One of: 'accident', 'waterlogging', 'vip_movement',
                       'signal_failure', 'construction'.
        severity: One of: 'low', 'medium', 'high', 'critical'.
        description: Optional human-readable description of the incident.

    Returns:
        Dict with the created incident details including affected junctions
        and routes. Returns error dict if location not found or invalid type.
    """
    valid_types = {"accident", "waterlogging", "vip_movement", "signal_failure", "construction"}
    valid_severities = {"low", "medium", "high", "critical"}

    if incident_type not in valid_types:
        return {
            "error": f"Invalid incident_type '{incident_type}'.",
            "valid_types": sorted(valid_types),
        }
    if severity not in valid_severities:
        return {
            "error": f"Invalid severity '{severity}'.",
            "valid_severities": sorted(valid_severities),
        }

    # Resolve zone from location
    zone_data = get_zone(location)
    if zone_data is None:
        available = list_all_zones()
        return {
            "error": f"Location '{location}' could not be resolved to a known zone.",
            "available_zones": available,
        }

    # Find affected junctions in this zone
    affected_junctions_data = get_junctions_in_zone(zone_data.zone)
    affected_junction_ids = [j.junction_id for j in affected_junctions_data]

    # Find affected routes
    affected_route_ids = [r.route_id for r in zone_data.routes]

    # Estimate clearance time based on severity
    clearance_map = {"low": 15, "medium": 30, "high": 60, "critical": 120}

    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"

    incident = Incident(
        incident_id=incident_id,
        location=location,
        zone=zone_data.zone,
        lat=zone_data.zone_center_lat,
        lng=zone_data.zone_center_lng,
        incident_type=incident_type,
        severity=severity,
        affected_junctions=affected_junction_ids,
        affected_routes=affected_route_ids,
        estimated_clearance_minutes=clearance_map[severity],
        description=description or f"{incident_type.replace('_', ' ').title()} reported at {location}",
    )

    _active_incidents[incident_id] = incident

    return {
        "status": "incident_created",
        "incident": incident.model_dump(),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@mcp.tool()
def get_active_incidents() -> dict[str, Any]:
    """Get all currently active incidents.

    Returns:
        Dict with list of all active incidents and their details.
    """
    return {
        "count": len(_active_incidents),
        "incidents": [inc.model_dump() for inc in _active_incidents.values()],
    }


@mcp.tool()
def list_zones() -> dict[str, Any]:
    """List all available zones with their coordinates.

    Returns:
        Dict with all zone names and center coordinates.
    """
    zones = list_all_zones()
    return {
        "count": len(zones),
        "zones": zones,
    }


@mcp.tool()
def list_junctions() -> dict[str, Any]:
    """List all available junctions with their IDs and names.

    Returns:
        Dict with all junction IDs and names.
    """
    junctions = list_all_junctions()
    return {
        "count": len(junctions),
        "junctions": junctions,
    }


# --- HTTP/SSE app for curl testing ---

# FastMCP can generate a Starlette/ASGI app for SSE transport
http_app = mcp.sse_app()


if __name__ == "__main__":
    # When run directly, use stdio transport (for ADK agent connection)
    mcp.run(transport="stdio")
