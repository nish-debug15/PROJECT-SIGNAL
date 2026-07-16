'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import AgentTracePanel from '@/components/AgentTracePanel';

// Dynamically import MapView with SSR disabled to prevent Leaflet window errors
const MapView = dynamic(() => import('@/components/MapView'), { ssr: false });

export default function Home() {
  return (
    <div className="dashboard-container">
      <AgentTracePanel />
      <div className="map-container">
        <MapView />
      </div>
    </div>
  );
}
