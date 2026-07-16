"""
Synthetic Bengaluru traffic data for SIGNAL MCP server.

This module provides realistic zone, route, junction, and incident data
modeled on actual Bengaluru geography. It serves as the default data source
until real BMTC GTFS data is swapped in by Jaineesh.

DATA STATUS: SYNTHETIC — do not mark Block 1 test gate as passed
until real GTFS data is loaded and re-verified.
"""

from pydantic import BaseModel
from typing import Optional


# --- Pydantic models for tool I/O ---

class RouteInfo(BaseModel):
    route_id: str
    route_short_name: str
    route_long_name: str
    stops: list[str]
    frequency_minutes: int
    is_active: bool = True


class ZoneRoutes(BaseModel):
    zone: str
    zone_center_lat: float
    zone_center_lng: float
    routes: list[RouteInfo]
    adjacent_zones: list[str]


class SignalPhase(BaseModel):
    direction: str
    green_seconds: int
    yellow_seconds: int = 3
    red_seconds: int


class JunctionSignalState(BaseModel):
    junction_id: str
    junction_name: str
    lat: float
    lng: float
    zone: str
    phases: list[SignalPhase]
    cycle_time_seconds: int
    is_adaptive: bool = False
    current_congestion: str  # "low", "moderate", "high", "critical"


class Incident(BaseModel):
    incident_id: str
    location: str
    zone: str
    lat: float
    lng: float
    incident_type: str  # "accident", "waterlogging", "vip_movement", "signal_failure", "construction"
    severity: str  # "low", "medium", "high", "critical"
    affected_junctions: list[str]
    affected_routes: list[str]
    estimated_clearance_minutes: Optional[int] = None
    description: str


# --- Synthetic zone/route data ---

ZONES: dict[str, ZoneRoutes] = {
    "marathahalli": ZoneRoutes(
        zone="marathahalli",
        zone_center_lat=12.9591,
        zone_center_lng=77.6974,
        adjacent_zones=["whitefield", "kr_puram", "indiranagar", "bellandur"],
        routes=[
            RouteInfo(
                route_id="BMTC-500D",
                route_short_name="500D",
                route_long_name="Kempegowda Bus Station → Whitefield (via Marathahalli)",
                stops=["Kempegowda BS", "Shivajinagar", "Indiranagar", "Marathahalli Bridge", "Kundalahalli", "ITPL", "Whitefield"],
                frequency_minutes=10,
            ),
            RouteInfo(
                route_id="BMTC-500C",
                route_short_name="500C",
                route_long_name="Kempegowda BS → ITPL (via Old Airport Road)",
                stops=["Kempegowda BS", "Trinity", "Old Airport Road", "Marathahalli", "ITPL"],
                frequency_minutes=12,
            ),
            RouteInfo(
                route_id="BMTC-KBS-MHL",
                route_short_name="335E",
                route_long_name="Banashankari → Marathahalli",
                stops=["Banashankari", "Jayanagar", "Koramangala", "Silk Board", "HSR Layout", "Bellandur", "Marathahalli"],
                frequency_minutes=15,
            ),
            RouteInfo(
                route_id="BMTC-MHL-KRP",
                route_short_name="317A",
                route_long_name="Marathahalli → KR Puram",
                stops=["Marathahalli Bridge", "Varthur Road Junction", "Kundalahalli Gate", "KR Puram Railway Station"],
                frequency_minutes=20,
            ),
        ],
    ),
    "silk_board": ZoneRoutes(
        zone="silk_board",
        zone_center_lat=12.9172,
        zone_center_lng=77.6228,
        adjacent_zones=["koramangala", "hsr_layout", "bellandur", "btm_layout", "madiwala"],
        routes=[
            RouteInfo(
                route_id="BMTC-500A",
                route_short_name="500A",
                route_long_name="Kempegowda BS → Electronic City (via Silk Board)",
                stops=["Kempegowda BS", "Shantinagar", "Madiwala", "Silk Board Junction", "Bommanahalli", "Electronic City Phase 1"],
                frequency_minutes=8,
            ),
            RouteInfo(
                route_id="BMTC-356",
                route_short_name="356",
                route_long_name="BTM Layout → Silk Board → Bellandur",
                stops=["BTM Layout", "Silk Board Junction", "HSR Layout", "Bellandur", "Marathahalli"],
                frequency_minutes=12,
            ),
            RouteInfo(
                route_id="BMTC-EC-SB",
                route_short_name="500E",
                route_long_name="Electronic City → Silk Board → KR Market",
                stops=["Electronic City Phase 2", "Bommanahalli", "Silk Board Junction", "Madiwala", "KR Market"],
                frequency_minutes=10,
            ),
        ],
    ),
    "kr_puram": ZoneRoutes(
        zone="kr_puram",
        zone_center_lat=13.0073,
        zone_center_lng=77.6963,
        adjacent_zones=["marathahalli", "whitefield", "hebbal", "tin_factory"],
        routes=[
            RouteInfo(
                route_id="BMTC-KRP-MBS",
                route_short_name="401",
                route_long_name="KR Puram → Majestic Bus Station",
                stops=["KR Puram", "Tin Factory", "Banaswadi", "Kammanahalli", "Shivajinagar", "Majestic"],
                frequency_minutes=10,
            ),
            RouteInfo(
                route_id="BMTC-KRP-WF",
                route_short_name="401K",
                route_long_name="KR Puram → Whitefield",
                stops=["KR Puram Railway Station", "Mahadevapura", "ITPL Main Gate", "Whitefield Bus Depot"],
                frequency_minutes=15,
            ),
        ],
    ),
    "koramangala": ZoneRoutes(
        zone="koramangala",
        zone_center_lat=12.9352,
        zone_center_lng=77.6245,
        adjacent_zones=["silk_board", "indiranagar", "madiwala", "btm_layout"],
        routes=[
            RouteInfo(
                route_id="BMTC-201R",
                route_short_name="201R",
                route_long_name="Koramangala → Majestic",
                stops=["Koramangala 4th Block", "Forum Mall", "Ejipura", "Domlur", "MG Road", "Majestic"],
                frequency_minutes=12,
            ),
            RouteInfo(
                route_id="BMTC-KRM-IND",
                route_short_name="340",
                route_long_name="Koramangala → Indiranagar",
                stops=["Koramangala Water Tank", "ST Bed Layout", "Ejipura", "Domlur", "Indiranagar 100ft Road"],
                frequency_minutes=18,
            ),
        ],
    ),
    "whitefield": ZoneRoutes(
        zone="whitefield",
        zone_center_lat=12.9698,
        zone_center_lng=77.7500,
        adjacent_zones=["marathahalli", "kr_puram"],
        routes=[
            RouteInfo(
                route_id="BMTC-500D",
                route_short_name="500D",
                route_long_name="Kempegowda Bus Station → Whitefield (via Marathahalli)",
                stops=["Kempegowda BS", "Shivajinagar", "Indiranagar", "Marathahalli Bridge", "ITPL", "Whitefield"],
                frequency_minutes=10,
            ),
            RouteInfo(
                route_id="BMTC-WF-MJ",
                route_short_name="500F",
                route_long_name="Whitefield → Majestic (via Old Madras Road)",
                stops=["Whitefield", "Hope Farm", "Varthur", "KR Puram", "Majestic"],
                frequency_minutes=20,
            ),
        ],
    ),
    "indiranagar": ZoneRoutes(
        zone="indiranagar",
        zone_center_lat=12.9784,
        zone_center_lng=77.6408,
        adjacent_zones=["marathahalli", "koramangala", "kr_puram"],
        routes=[
            RouteInfo(
                route_id="BMTC-500D",
                route_short_name="500D",
                route_long_name="Kempegowda BS → Whitefield (via Indiranagar)",
                stops=["Kempegowda BS", "Shivajinagar", "Indiranagar", "Marathahalli Bridge", "ITPL", "Whitefield"],
                frequency_minutes=10,
            ),
            RouteInfo(
                route_id="BMTC-IND-MJ",
                route_short_name="310",
                route_long_name="Indiranagar → Majestic",
                stops=["Indiranagar 100ft Road", "Ulsoor", "MG Road", "Shivajinagar", "Majestic"],
                frequency_minutes=10,
            ),
        ],
    ),
}


# --- Synthetic junction/signal data ---

JUNCTIONS: dict[str, JunctionSignalState] = {
    "J-MHL-01": JunctionSignalState(
        junction_id="J-MHL-01",
        junction_name="Marathahalli Bridge Junction",
        lat=12.9563,
        lng=77.7011,
        zone="marathahalli",
        cycle_time_seconds=120,
        current_congestion="high",
        phases=[
            SignalPhase(direction="ORR_northbound", green_seconds=40, red_seconds=77),
            SignalPhase(direction="ORR_southbound", green_seconds=40, red_seconds=77),
            SignalPhase(direction="varthur_road_east", green_seconds=25, red_seconds=92),
            SignalPhase(direction="varthur_road_west", green_seconds=25, red_seconds=92),
        ],
    ),
    "J-MHL-02": JunctionSignalState(
        junction_id="J-MHL-02",
        junction_name="Kundalahalli Gate Junction",
        lat=12.9620,
        lng=77.7150,
        zone="marathahalli",
        cycle_time_seconds=90,
        current_congestion="moderate",
        phases=[
            SignalPhase(direction="ORR_northbound", green_seconds=35, red_seconds=52),
            SignalPhase(direction="ORR_southbound", green_seconds=35, red_seconds=52),
            SignalPhase(direction="kundalahalli_road", green_seconds=20, red_seconds=67),
        ],
    ),
    "J-SB-01": JunctionSignalState(
        junction_id="J-SB-01",
        junction_name="Silk Board Junction",
        lat=12.9172,
        lng=77.6228,
        zone="silk_board",
        cycle_time_seconds=180,
        current_congestion="critical",
        phases=[
            SignalPhase(direction="hosur_road_north", green_seconds=50, red_seconds=127),
            SignalPhase(direction="hosur_road_south", green_seconds=50, red_seconds=127),
            SignalPhase(direction="orr_east_to_bellandur", green_seconds=40, red_seconds=137),
            SignalPhase(direction="orr_west_to_btm", green_seconds=40, red_seconds=137),
        ],
    ),
    "J-SB-02": JunctionSignalState(
        junction_id="J-SB-02",
        junction_name="Bommanahalli Junction",
        lat=12.9083,
        lng=77.6183,
        zone="silk_board",
        cycle_time_seconds=120,
        current_congestion="high",
        phases=[
            SignalPhase(direction="hosur_road_north", green_seconds=40, red_seconds=77),
            SignalPhase(direction="hosur_road_south", green_seconds=40, red_seconds=77),
            SignalPhase(direction="begur_road", green_seconds=20, red_seconds=97),
        ],
    ),
    "J-KRP-01": JunctionSignalState(
        junction_id="J-KRP-01",
        junction_name="KR Puram Railway Junction",
        lat=13.0073,
        lng=77.6963,
        zone="kr_puram",
        cycle_time_seconds=120,
        current_congestion="moderate",
        phases=[
            SignalPhase(direction="old_madras_road_west", green_seconds=40, red_seconds=77),
            SignalPhase(direction="old_madras_road_east", green_seconds=40, red_seconds=77),
            SignalPhase(direction="railway_station_road", green_seconds=25, red_seconds=92),
        ],
    ),
    "J-KRM-01": JunctionSignalState(
        junction_id="J-KRM-01",
        junction_name="Koramangala Water Tank Junction",
        lat=12.9352,
        lng=77.6245,
        zone="koramangala",
        cycle_time_seconds=90,
        current_congestion="moderate",
        phases=[
            SignalPhase(direction="80ft_road_north", green_seconds=30, red_seconds=57),
            SignalPhase(direction="80ft_road_south", green_seconds=30, red_seconds=57),
            SignalPhase(direction="st_bed_road", green_seconds=20, red_seconds=67),
        ],
    ),
    "J-IND-01": JunctionSignalState(
        junction_id="J-IND-01",
        junction_name="Indiranagar 100ft Road Junction",
        lat=12.9784,
        lng=77.6408,
        zone="indiranagar",
        cycle_time_seconds=90,
        current_congestion="moderate",
        phases=[
            SignalPhase(direction="100ft_road_east", green_seconds=30, red_seconds=57),
            SignalPhase(direction="100ft_road_west", green_seconds=30, red_seconds=57),
            SignalPhase(direction="12th_main", green_seconds=20, red_seconds=67),
        ],
    ),
    "J-WF-01": JunctionSignalState(
        junction_id="J-WF-01",
        junction_name="Whitefield Main Road Junction",
        lat=12.9698,
        lng=77.7500,
        zone="whitefield",
        cycle_time_seconds=90,
        current_congestion="low",
        phases=[
            SignalPhase(direction="whitefield_main_north", green_seconds=35, red_seconds=52),
            SignalPhase(direction="whitefield_main_south", green_seconds=35, red_seconds=52),
            SignalPhase(direction="itpl_road", green_seconds=20, red_seconds=67),
        ],
    ),
}


# Lookup helpers
def get_zone(zone_name: str) -> ZoneRoutes | None:
    """Get zone data, case-insensitive fuzzy match."""
    key = zone_name.lower().strip().replace(" ", "_").replace("-", "_")
    if key in ZONES:
        return ZONES[key]
    # Try partial match
    for k, v in ZONES.items():
        if key in k or k in key:
            return v
    return None


def get_junction(junction_id: str) -> JunctionSignalState | None:
    """Get junction data by ID, case-insensitive."""
    key = junction_id.upper().strip()
    if key in JUNCTIONS:
        return JUNCTIONS[key]
    # Try partial match on name
    for k, v in JUNCTIONS.items():
        if key in k or junction_id.lower() in v.junction_name.lower():
            return v
    return None


def get_junctions_in_zone(zone_name: str) -> list[JunctionSignalState]:
    """Get all junctions in a zone."""
    key = zone_name.lower().strip().replace(" ", "_").replace("-", "_")
    return [j for j in JUNCTIONS.values() if j.zone == key]


def list_all_zones() -> list[str]:
    """List all available zone names."""
    return list(ZONES.keys())


def list_all_junctions() -> list[str]:
    """List all available junction IDs with names."""
    return [f"{j.junction_id}: {j.junction_name}" for j in JUNCTIONS.values()]
