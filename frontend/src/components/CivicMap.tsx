import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Issue } from '../types';
import { AlertTriangle, MapPin, Eye, Table } from 'lucide-react';

interface CivicMapProps {
  issues: Issue[];
  selectedIssue?: Issue | null;
  onSelectIssue?: (issue: Issue) => void;
  // Picker mode for public reporting
  pickerMode?: boolean;
  selectedCoordinates?: { lat: number; lng: number } | null;
  onCoordinatesChange?: (coords: { lat: number; lng: number }) => void;
  height?: string;
}

export const CivicMap: React.FC<CivicMapProps> = ({
  issues,
  selectedIssue,
  onSelectIssue,
  pickerMode = false,
  selectedCoordinates,
  onCoordinatesChange,
  height = '480px',
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const pickerMarkerRef = useRef<L.Marker | null>(null);
  const [mapError, setMapError] = useState(false);
  const [showTableFallback, setShowTableFallback] = useState(false);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    try {
      const defaultCenter: L.LatLngTuple = selectedCoordinates
        ? [selectedCoordinates.lat, selectedCoordinates.lng]
        : issues.length > 0
        ? [issues[0].latitude, issues[0].longitude]
        : [37.7749, -122.4194];

      const map = L.map(mapContainerRef.current, {
        center: defaultCenter,
        zoom: 13,
      });

      // Standard OpenStreetMap tiles (free civic educational usage)
      const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors | CivicPulse Platform',
        maxZoom: 18,
      });

      tileLayer.on('tileerror', () => {
        setMapError(true);
      });

      tileLayer.addTo(map);

      const markersLayer = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
      markersLayerRef.current = markersLayer;

      // Click listener for location picking in report form
      if (pickerMode && onCoordinatesChange) {
        map.on('click', (e: L.LeafletMouseEvent) => {
          onCoordinatesChange({ lat: e.latlng.lat, lng: e.latlng.lng });
        });
      }
    } catch (err) {
      console.error('Failed to initialize Leaflet map:', err);
      setMapError(true);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Handle picker marker updates
  useEffect(() => {
    if (!mapInstanceRef.current || !pickerMode) return;

    if (selectedCoordinates) {
      if (!pickerMarkerRef.current) {
        const pickerIcon = L.divIcon({
          className: 'custom-picker-pin',
          html: `<div style="background-color: #0d9488; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 2px solid white; font-weight: bold;">📍</div>`,
          iconSize: [28, 28],
          iconAnchor: [14, 28],
        });
        pickerMarkerRef.current = L.marker([selectedCoordinates.lat, selectedCoordinates.lng], {
          icon: pickerIcon,
          draggable: true,
        }).addTo(mapInstanceRef.current);

        pickerMarkerRef.current.on('dragend', (e) => {
          const marker = e.target as L.Marker;
          const pos = marker.getLatLng();
          if (onCoordinatesChange) onCoordinatesChange({ lat: pos.lat, lng: pos.lng });
        });
      } else {
        pickerMarkerRef.current.setLatLng([selectedCoordinates.lat, selectedCoordinates.lng]);
      }
      mapInstanceRef.current.panTo([selectedCoordinates.lat, selectedCoordinates.lng]);
    }
  }, [selectedCoordinates, pickerMode]);

  // Update Issue Markers
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current || pickerMode) return;

    markersLayerRef.current.clearLayers();

    issues.forEach((issue) => {
      // Color-code marker based on priority and status
      let pinColor = '#0284c7'; // default blue
      if (issue.status === 'Resolved' || issue.status === 'Verified') {
        pinColor = '#10b981'; // green
      } else if (issue.safety_hazard || issue.priority_score >= 70) {
        pinColor = '#e11d48'; // red critical
      } else if (issue.priority_score >= 45) {
        pinColor = '#d97706'; // amber warning
      }

      const customIcon = L.divIcon({
        className: 'custom-civic-pin',
        html: `<div style="background-color: ${pinColor}; color: white; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 2px solid white; font-size: 11px; font-weight: bold;">
          ${issue.priority_score ? Math.round(issue.priority_score) : '!'}
        </div>`,
        iconSize: [26, 26],
        iconAnchor: [13, 26],
        popupAnchor: [0, -24],
      });

      const marker = L.marker([issue.latitude, issue.longitude], { icon: customIcon });

      const popupHtml = `
        <div style="font-family: inherit; min-width: 180px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-size: 10px; font-weight: 700; color: #64748b;">${issue.public_reference}</span>
            <span style="font-size: 10px; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-weight: 600;">${issue.status}</span>
          </div>
          <div style="font-weight: 700; font-size: 13px; color: #0f172a; margin-bottom: 4px;">${issue.title}</div>
          <div style="font-size: 11px; color: #475569; margin-bottom: 6px;">${issue.ward_or_district || 'Zone'}</div>
          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 600;">
            <span style="color: ${pinColor}">Priority: ${Math.round(issue.priority_score)}</span>
            <span style="color: #0d9488;">${issue.category?.name || 'Issue'}</span>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);

      marker.on('click', () => {
        if (onSelectIssue) onSelectIssue(issue);
      });

      markersLayerRef.current?.addLayer(marker);
    });
  }, [issues, pickerMode]);

  return (
    <div className="relative w-full rounded-xl overflow-hidden border border-slate-200 shadow-sm bg-white">
      {/* Map Header Toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 border-b border-slate-200 text-xs text-slate-600">
        <div className="flex items-center gap-2 font-medium">
          <MapPin className="w-4 h-4 text-teal-600" />
          <span>{pickerMode ? 'Click anywhere on map to position pin' : `Civic Issues Map (${issues.length} points plotted)`}</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowTableFallback(!showTableFallback)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition"
          >
            <Table className="w-3.5 h-3.5" />
            <span>{showTableFallback ? 'Show Map' : 'Table View'}</span>
          </button>
        </div>
      </div>

      {/* Map Unavailable Banner */}
      {mapError && (
        <div className="p-3 bg-amber-50 border-b border-amber-200 text-amber-800 text-xs flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 flex-shrink-0 text-amber-600" />
          <span>External map tile service unavailable. Switching to tabular view automatically.</span>
        </div>
      )}

      {/* Tabular Fallback or Interactive Map */}
      {showTableFallback || mapError ? (
        <div className="overflow-x-auto p-4 max-h-[480px]">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-100 text-slate-800 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th className="p-2.5">Reference</th>
                <th className="p-2.5">Category</th>
                <th className="p-2.5">Title</th>
                <th className="p-2.5">Area / Ward</th>
                <th className="p-2.5">Status</th>
                <th className="p-2.5">Priority</th>
                <th className="p-2.5">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {issues.map((i) => (
                <tr key={i.id} className="hover:bg-slate-50">
                  <td className="p-2.5 font-mono font-bold text-slate-900">{i.public_reference}</td>
                  <td className="p-2.5">{i.category?.name}</td>
                  <td className="p-2.5 font-medium text-slate-900">{i.title}</td>
                  <td className="p-2.5">{i.ward_or_district}</td>
                  <td className="p-2.5">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-200 text-slate-800">
                      {i.status}
                    </span>
                  </td>
                  <td className="p-2.5 font-bold text-teal-700">{Math.round(i.priority_score)}</td>
                  <td className="p-2.5">
                    <button
                      onClick={() => onSelectIssue && onSelectIssue(i)}
                      className="text-teal-600 hover:text-teal-800 font-medium"
                    >
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div ref={mapContainerRef} style={{ height, width: '100%' }} />
      )}
    </div>
  );
};
