'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import AgentTracePanel from '@/components/AgentTracePanel';

// Dynamically import MapView with SSR disabled to prevent Leaflet window errors
const MapView = dynamic(() => import('@/components/MapView'), { ssr: false });

// Pre-defined incident scenarios covering different incident types across Bangalore
const SCENARIOS = [
  {
    label: "Waterlogging — Koramangala",
    desc: "CRITICAL: Waterlogging at Koramangala Water Tank Junction. Storm drains overflowing, 2 lanes submerged.",
    type: "waterlogging",
  },
  {
    label: "Accident — Hebbal Flyover",
    desc: "HIGH: Multi-vehicle pile-up on Hebbal Flyover northbound. 3 lanes blocked, emergency vehicles on scene.",
    type: "accident",
  },
  {
    label: "Signal Failure — MG Road",
    desc: "CRITICAL: Complete signal failure at MG Road–Brigade Road junction. Manual traffic control deployed.",
    type: "signal_failure",
  },
  {
    label: "VIP Movement — Vidhana Soudha",
    desc: "HIGH: VIP convoy movement from Vidhana Soudha to HAL Airport. Full road closure on Cubbon Road and MG Road for 45 minutes.",
    type: "vip_movement",
  },
  {
    label: "Construction — Whitefield",
    desc: "MEDIUM: Metro construction debris blocking 2 lanes on Whitefield Main Road near ITPL. Expected clearance 90 minutes.",
    type: "construction",
  },
  {
    label: "Flooding — Silk Board",
    desc: "CRITICAL: Severe flooding at Silk Board Junction underpass. All vehicular movement halted. BBMP pumps deployed.",
    type: "waterlogging",
  },
];

export default function Home() {
  const [isTriggering, setIsTriggering] = useState(false);
  const [showPanel, setShowPanel] = useState(false);
  // Incremented on each trigger to signal AgentTracePanel to clear
  const [runCounter, setRunCounter] = useState(0);

  const handleTrigger = async (scenarioDesc: string) => {
    setShowPanel(false);
    setIsTriggering(true);
    // Bump counter to tell trace panel to clear previous entries
    setRunCounter(prev => prev + 1);

    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws/logs';
      const apiUrl = wsUrl.replace('wss://', 'https://').replace('ws://', 'http://').replace('/ws/logs', '/api/incident');

      await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incident_desc: scenarioDesc })
      });
    } catch (err) {
      console.error("Failed to trigger incident", err);
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div className="dashboard-container">
      <AgentTracePanel runCounter={runCounter} />
      <div className="map-container" style={{ position: 'relative' }}>
        <MapView />

        {/* Scenario Picker Panel */}
        {showPanel && (
          <div className="scenario-panel mono">
            <div className="scenario-panel-header">Select Incident Scenario</div>
            {SCENARIOS.map((s, i) => (
              <button
                key={i}
                className="scenario-btn"
                onClick={() => handleTrigger(s.desc)}
              >
                <span className={`scenario-type-dot type-${s.type}`} />
                <span className="scenario-label">{s.label}</span>
              </button>
            ))}
          </div>
        )}

        {/* Trigger Button */}
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
