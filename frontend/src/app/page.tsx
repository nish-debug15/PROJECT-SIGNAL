'use client';

import React, { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import AgentTracePanel from '@/components/AgentTracePanel';

const MapView = dynamic(() => import('@/components/MapView'), { ssr: false });

// Each scenario carries its own map visualization data
export interface ScenarioMapData {
  incident: { lat: number; lng: number; label: string };
  impactRadius: number;
  junctions: { lat: number; lng: number; label: string; id: string; status: string }[];
  blockedRoute: [number, number][];
  approvedRoute: [number, number][];
  mapCenter: [number, number];
  zoom: number;
}

export interface Scenario {
  label: string;
  desc: string;
  type: string;
  map: ScenarioMapData;
}

const SCENARIOS: Scenario[] = [
  {
    label: "Waterlogging — Koramangala",
    desc: "CRITICAL: Waterlogging at Koramangala Water Tank Junction. Storm drains overflowing, 2 lanes submerged.",
    type: "waterlogging",
    map: {
      incident: { lat: 12.9352, lng: 77.6245, label: "Waterlogging — Koramangala Water Tank" },
      impactRadius: 2500,
      junctions: [
        { lat: 12.9172, lng: 77.6228, label: "Silk Board Junction", id: "J-SB-01", status: "AVOID" },
        { lat: 12.9563, lng: 77.7011, label: "Marathahalli Bridge", id: "J-MHL-01", status: "REROUTE TARGET" },
      ],
      blockedRoute: [[12.9352, 77.6245], [12.9280, 77.6230], [12.9172, 77.6228]],
      approvedRoute: [[12.9352, 77.6245], [12.9380, 77.6350], [12.9450, 77.6600], [12.9563, 77.7011]],
      mapCenter: [12.945, 77.66],
      zoom: 12,
    },
  },
  {
    label: "Accident — Hebbal Flyover",
    desc: "HIGH: Multi-vehicle pile-up on Hebbal Flyover northbound. 3 lanes blocked, emergency vehicles on scene.",
    type: "accident",
    map: {
      incident: { lat: 13.0358, lng: 77.5970, label: "Multi-vehicle accident — Hebbal Flyover" },
      impactRadius: 2000,
      junctions: [
        { lat: 13.0280, lng: 77.5890, label: "Mekhri Circle", id: "J-MK-01", status: "CONGESTED" },
        { lat: 13.0450, lng: 77.6120, label: "Esteem Mall Junction", id: "J-EM-01", status: "REROUTE TARGET" },
      ],
      blockedRoute: [[13.0358, 77.5970], [13.0320, 77.5940], [13.0280, 77.5890]],
      approvedRoute: [[13.0358, 77.5970], [13.0400, 77.6050], [13.0450, 77.6120], [13.0500, 77.6200]],
      mapCenter: [13.038, 77.60],
      zoom: 13,
    },
  },
  {
    label: "Signal Failure — MG Road",
    desc: "CRITICAL: Complete signal failure at MG Road–Brigade Road junction. Manual traffic control deployed.",
    type: "signal_failure",
    map: {
      incident: { lat: 12.9750, lng: 77.6060, label: "Signal Failure — MG Road × Brigade Road" },
      impactRadius: 1500,
      junctions: [
        { lat: 12.9720, lng: 77.6100, label: "Trinity Circle", id: "J-TR-01", status: "CONGESTED" },
        { lat: 12.9810, lng: 77.5990, label: "Cubbon Park Junction", id: "J-CP-01", status: "REROUTE TARGET" },
      ],
      blockedRoute: [[12.9750, 77.6060], [12.9730, 77.6080], [12.9720, 77.6100]],
      approvedRoute: [[12.9750, 77.6060], [12.9780, 77.6020], [12.9810, 77.5990], [12.9850, 77.5950]],
      mapCenter: [12.977, 77.603],
      zoom: 14,
    },
  },
  {
    label: "VIP Movement — Vidhana Soudha",
    desc: "HIGH: VIP convoy movement from Vidhana Soudha to HAL Airport. Full road closure on Cubbon Road and MG Road for 45 minutes.",
    type: "vip_movement",
    map: {
      incident: { lat: 12.9791, lng: 77.5913, label: "VIP Convoy — Vidhana Soudha" },
      impactRadius: 3000,
      junctions: [
        { lat: 12.9750, lng: 77.6060, label: "MG Road Junction", id: "J-MG-01", status: "CLOSED" },
        { lat: 12.9600, lng: 77.6480, label: "HAL Airport Road", id: "J-HAL-01", status: "REROUTE TARGET" },
      ],
      blockedRoute: [[12.9791, 77.5913], [12.9750, 77.6060], [12.9700, 77.6300], [12.9600, 77.6480]],
      approvedRoute: [[12.9791, 77.5913], [12.9650, 77.5850], [12.9550, 77.6100], [12.9500, 77.6350], [12.9600, 77.6480]],
      mapCenter: [12.970, 77.615],
      zoom: 13,
    },
  },
  {
    label: "Construction — Whitefield",
    desc: "MEDIUM: Metro construction debris blocking 2 lanes on Whitefield Main Road near ITPL. Expected clearance 90 minutes.",
    type: "construction",
    map: {
      incident: { lat: 12.9698, lng: 77.7500, label: "Metro Construction — Whitefield Main Rd" },
      impactRadius: 2000,
      junctions: [
        { lat: 12.9770, lng: 77.7400, label: "ITPL Junction", id: "J-IT-01", status: "CONGESTED" },
        { lat: 12.9563, lng: 77.7011, label: "Marathahalli Bridge", id: "J-MHL-01", status: "REROUTE TARGET" },
      ],
      blockedRoute: [[12.9698, 77.7500], [12.9720, 77.7450], [12.9770, 77.7400]],
      approvedRoute: [[12.9698, 77.7500], [12.9650, 77.7350], [12.9600, 77.7150], [12.9563, 77.7011]],
      mapCenter: [12.965, 77.725],
      zoom: 13,
    },
  },
  {
    label: "Flooding — Silk Board",
    desc: "CRITICAL: Severe flooding at Silk Board Junction underpass. All vehicular movement halted. BBMP pumps deployed.",
    type: "waterlogging",
    map: {
      incident: { lat: 12.9172, lng: 77.6228, label: "Severe Flooding — Silk Board Underpass" },
      impactRadius: 2500,
      junctions: [
        { lat: 12.9280, lng: 77.6310, label: "BTM Layout Junction", id: "J-BTM-01", status: "CONGESTED" },
        { lat: 12.9352, lng: 77.6245, label: "Koramangala Junction", id: "J-KRM-01", status: "REROUTE TARGET" },
      ],
      blockedRoute: [[12.9172, 77.6228], [12.9220, 77.6260], [12.9280, 77.6310]],
      approvedRoute: [[12.9172, 77.6228], [12.9100, 77.6300], [12.9150, 77.6500], [12.9300, 77.6600], [12.9450, 77.6600]],
      mapCenter: [12.928, 77.64],
      zoom: 13,
    },
  },
];

export default function Home() {
  const [isTriggering, setIsTriggering] = useState(false);
  const [showPanel, setShowPanel] = useState(false);
  const [runCounter, setRunCounter] = useState(0);
  // null = no scenario active, show empty map
  const [activeScenario, setActiveScenario] = useState<Scenario | null>(null);
  // Controls whether the approved route is shown (only after APPROVE)
  const [showApprovedRoute, setShowApprovedRoute] = useState(false);

  const handleApproved = useCallback(() => {
    setShowApprovedRoute(true);
  }, []);

  const handleTrigger = async (scenario: Scenario) => {
    setShowPanel(false);
    setIsTriggering(true);
    setRunCounter(prev => prev + 1);
    setActiveScenario(scenario);
    setShowApprovedRoute(false);

    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws/logs';
      const apiUrl = wsUrl.replace('wss://', 'https://').replace('ws://', 'http://').replace('/ws/logs', '/api/incident');

      await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incident_desc: scenario.desc })
      });
    } catch (err) {
      console.error("Failed to trigger incident", err);
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div className="dashboard-container">
      <AgentTracePanel runCounter={runCounter} onApproved={handleApproved} />
      <div className="map-container" style={{ position: 'relative' }}>
        <MapView scenario={activeScenario} showApprovedRoute={showApprovedRoute} />

        {showPanel && (
          <div className="scenario-panel mono">
            <div className="scenario-panel-header">Select Incident Scenario</div>
            {SCENARIOS.map((s, i) => (
              <button
                key={i}
                className="scenario-btn"
                onClick={() => handleTrigger(s)}
              >
                <span className={`scenario-type-dot type-${s.type}`} />
                <span className="scenario-label">{s.label}</span>
              </button>
            ))}
          </div>
        )}

        <button
          onClick={() => setShowPanel(prev => !prev)}
          disabled={isTriggering}
          className="trigger-btn mono"
        >
          {isTriggering ? 'PROCESSING...' : '🚨 TRIGGER INCIDENT'}
        </button>
      </div>
    </div>
  );
}
