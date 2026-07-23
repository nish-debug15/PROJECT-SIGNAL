'use client';

import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import type { Scenario } from '@/app/page';

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

const IncidentIcon = L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: #EF4444; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #fff; box-shadow: 0 0 10px #EF4444;"></div>`,
  iconSize: [14, 14],
  iconAnchor: [7, 7]
});

const JunctionIcon = (status: string) => L.divIcon({
  className: 'custom-div-icon',
  html: `<div style="background-color: ${status === 'REROUTE TARGET' ? '#10B981' : status === 'CLOSED' ? '#EF4444' : '#F59E0B'}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid #fff;"></div>`,
  iconSize: [12, 12],
  iconAnchor: [6, 6]
});

interface MapViewProps {
  scenario: Scenario | null;
  showApprovedRoute: boolean;
}

export default function MapView({ scenario, showApprovedRoute }: MapViewProps) {
  // Default center: Bangalore overview
  const center: [number, number] = scenario ? scenario.map.mapCenter : [12.9716, 77.5946];
  const zoom = scenario ? scenario.map.zoom : 12;

  return (
    <div style={{ position: 'relative', height: '100%', width: '100%' }}>
      {/* Legend Overlay */}
      <div style={{ position: 'absolute', bottom: 20, left: 20, zIndex: 1000, background: 'rgba(10,10,10,0.85)', padding: '12px', borderRadius: '6px', border: '1px solid #333', color: '#fff', fontSize: '12px' }} className="mono">
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#EF4444', border: '2px solid #fff', marginRight: 8 }}></div> Incident
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ width: 12, height: 12, borderRadius: '50%', background: 'rgba(239, 68, 68, 0.2)', border: '2px solid rgba(239, 68, 68, 0.5)', marginRight: 8 }}></div> Impact Zone
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ width: 15, height: 2, borderBottom: '3px solid #EF4444', marginRight: 8, opacity: 0.6 }}></div> Rejected Route
        </div>
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ width: 15, height: 2, borderBottom: '3px dashed #10B981', marginRight: 8 }}></div> Approved Reroute
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ width: 12, height: 12, borderRadius: '50%', background: '#F59E0B', border: '2px solid #fff', marginRight: 8 }}></div> Affected Junction
        </div>
      </div>

      <MapContainer key={scenario ? scenario.label : 'default'} center={center} zoom={zoom} style={{ height: '100%', width: '100%', background: '#0a0a0a' }} zoomControl={false}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {scenario && (
          <>
            {/* Impact Zone */}
            <Circle
              center={[scenario.map.incident.lat, scenario.map.incident.lng]}
              radius={scenario.map.impactRadius}
              pathOptions={{ color: '#EF4444', fillColor: '#EF4444', fillOpacity: 0.1, weight: 1, dashArray: '4' }}
            >
              <Tooltip direction="top" offset={[0, -20]} opacity={0.9} permanent className="mono">
                {scenario.map.incident.label}
              </Tooltip>
            </Circle>

            {/* Incident Marker */}
            <Marker position={[scenario.map.incident.lat, scenario.map.incident.lng]} icon={IncidentIcon}>
              <Popup className="mono">
                <strong style={{ color: '#EF4444' }}>{scenario.map.incident.label}</strong>
              </Popup>
            </Marker>

            {/* Blocked Route (always shown — the rejected path) */}
            <Polyline
              positions={scenario.map.blockedRoute}
              pathOptions={{ color: '#EF4444', weight: 3, opacity: 0.5, dashArray: '8, 8' }}
            />

            {/* Approved Reroute (shown only after verifier approves) */}
            {showApprovedRoute && (
              <Polyline
                positions={scenario.map.approvedRoute}
                pathOptions={{ color: '#10B981', weight: 4, dashArray: '5, 10' }}
              />
            )}

            {/* Junction Markers */}
            {scenario.map.junctions.map((j, i) => (
              <Marker key={i} position={[j.lat, j.lng]} icon={JunctionIcon(j.status)}>
                <Popup className="mono">
                  <strong style={{ color: j.status === 'REROUTE TARGET' ? '#10B981' : '#F59E0B' }}>{j.status}</strong><br />
                  {j.id}<br />
                  {j.label}
                </Popup>
              </Marker>
            ))}
          </>
        )}

        {/* Empty state — no scenario selected */}
        {!scenario && (
          <Marker position={[12.9716, 77.5946]}>
            <Popup className="mono">
              <strong>SIGNAL</strong><br />
              Select an incident to visualize
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
