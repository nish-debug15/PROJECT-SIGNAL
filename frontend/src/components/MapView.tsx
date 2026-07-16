'use client';

import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
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

const ZONES = [
  { name: 'Koramangala', lat: 12.9352, lng: 77.6245 },
  { name: 'Silk Board', lat: 12.9172, lng: 77.6228 },
  { name: 'Marathahalli', lat: 12.9591, lng: 77.6974 },
  { name: 'Whitefield', lat: 12.9698, lng: 77.7500 },
  { name: 'KR Puram', lat: 13.0073, lng: 77.6963 },
  { name: 'Indiranagar', lat: 12.9784, lng: 77.6408 },
];

export default function MapView() {
  const center: [number, number] = [12.945, 77.66]; // Center between Koramangala and Marathahalli

  return (
    <MapContainer center={center} zoom={12} style={{ height: '100%', width: '100%', background: '#0a0a0a' }} zoomControl={false}>
      {/* CartoDB Dark Matter Tile Layer (Placeholder) */}
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
      />

      {/* Render Zones as Circles */}
      {ZONES.map((zone) => (
        <Circle
          key={zone.name}
          center={[zone.lat, zone.lng]}
          radius={1500}
          pathOptions={{ color: '#374151', fillColor: '#1A1D24', fillOpacity: 0.4, weight: 1 }}
        >
          <Popup className="mono">{zone.name} Zone</Popup>
        </Circle>
      ))}

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
  );
}
