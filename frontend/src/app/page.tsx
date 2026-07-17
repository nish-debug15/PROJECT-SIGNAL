'use client';

import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import AgentTracePanel from '@/components/AgentTracePanel';

// Dynamically import MapView with SSR disabled to prevent Leaflet window errors
const MapView = dynamic(() => import('@/components/MapView'), { ssr: false });

export default function Home() {
  const [isTriggering, setIsTriggering] = useState(false);

  const handleTrigger = async () => {
    setIsTriggering(true);
    try {
      // Intelligently derive the API URL from the existing WebSocket environment variable
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8080/ws/logs';
      const apiUrl = wsUrl.replace('wss://', 'https://').replace('ws://', 'http://').replace('/ws/logs', '/api/incident');
      
      await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ incident_desc: "CRITICAL: Waterlogging at Koramangala Water Tank Junction" })
      });
    } catch (err) {
      console.error("Failed to trigger incident", err);
    } finally {
      setIsTriggering(false);
    }
  };

  return (
    <div className="dashboard-container">
      <AgentTracePanel />
      <div className="map-container" style={{ position: 'relative' }}>
        <MapView />
        <button 
          onClick={handleTrigger}
          disabled={isTriggering}
          className="mono"
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            zIndex: 1000,
            padding: '12px 24px',
            backgroundColor: '#EF4444',
            color: 'white',
            border: '2px solid #fff',
            borderRadius: '6px',
            fontWeight: 'bold',
            cursor: isTriggering ? 'not-allowed' : 'pointer',
            boxShadow: '0 0 15px rgba(239,68,68,0.5)',
            opacity: isTriggering ? 0.7 : 1,
            transition: 'all 0.2s ease'
          }}
        >
          {isTriggering ? 'TRIGGERING...' : '🚨 TRIGGER INCIDENT'}
        </button>
      </div>
    </div>
  );
}
