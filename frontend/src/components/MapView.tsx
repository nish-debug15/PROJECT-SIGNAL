'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in React-Leaflet
const iconUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png';
const iconRetinaUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png';
const shadowUrl = 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

// Custom icons for specific states
const IncidentIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #EF4444; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 0 10px #EF4444;"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

const JunctionIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #3B82F6; width: 12px; height: 12px; border-radius: 50%; border: 2px solid #fff;"></div>`,
  iconSize: [12, 12],
  iconAnchor: [6, 6]
});

const reroutePath: [number, number][] = [
  [12.9352, 77.6245], // Koramangala Water Tank
  [12.9380, 77.6350], // Turning towards ORR
  [12.9450, 77.6600], // Along ORR
  [12.9563, 77.7011]  // Marathahalli Bridge
];

export default function MapView() {
  const center: [number, number] = [12.945, 77.66]; // Center between Koramangala and Marathahalli

  return (
    <div style={{ position: 'relative', height: '100%', width: '100%' }}>
      {/* Legend Overlay */}
      <div style={{ position: 'absolute', bottom: 20, left: 20, zIndex: 1000, background: 'rgba(10,10,10,0.8)', padding: '12px', borderRadius: '6px', border: '1px solid #333', color: '#fff', fontSize: '12px' }} className="mono">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#EF4444', border: '2px solid #fff', marginRight: 8 }}></div> Incident
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ width: 12, height: 12, borderRadius: '50%', background: 'rgba(239, 68, 68, 0.2)', border: '2px solid rgba(239, 68, 68, 0.5)', marginRight: 8 }}></div> Impact Zone
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#3B82F6', border: '2px solid #fff', marginRight: 8 }}></div> Junction
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ width: 15, height: 2, borderBottom: '3px dashed #10B981', marginRight: 8 }}></div> Proposed Reroute
        </div>
      </div>

      <MapContainer center={center} zoom={12} style={{ height: '100%', width: '100%', background: '#0a0a0a' }} zoomControl={false}>
        {/* CartoDB Dark Matter Tile Layer (Placeholder) */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {/* Single Impact Zone */}
        <Circle
          center={[12.9352, 77.6245]}
          radius={2500}
          pathOptions={{ color: '#EF4444', fillColor: '#EF4444', fillOpacity: 0.1, weight: 1, dashArray: '4' }}
        >
          <Tooltip direction="top" offset={[0, -20]} opacity={0.9} permanent className="mono">
            Primary Impact Zone
          </Tooltip>
        </Circle>

        {/* Reroute Path */}
        <Polyline positions={reroutePath} pathOptions={{ color: '#10B981', weight: 4, dashArray: '5, 10' }} />

        {/* Koramangala Incident Marker */}
        <Marker position={[12.9352, 77.6245]} icon={IncidentIcon}>
          <Popup className="mono">
            <strong style={{ color: '#EF4444' }}>CRITICAL: Waterlogging</strong><br />
            J-KRM-01<br />
            Koramangala Water Tank Junction
          </Popup>
        </Marker>

        {/* Silk Board Junction Marker */}
        <Marker position={[12.9172, 77.6228]} icon={JunctionIcon}>
          <Popup className="mono">
            <strong style={{ color: '#F59E0B' }}>AVOID ROUTING</strong><br />
            J-SB-01<br />
            Silk Board Junction (Critical Congestion)
          </Popup>
        </Marker>
        
        {/* Marathahalli Bridge Junction Marker */}
        <Marker position={[12.9563, 77.7011]} icon={JunctionIcon}>
          <Popup className="mono">
            J-MHL-01<br />
            Marathahalli Bridge Junction
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
