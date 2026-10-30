import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Issue } from '../types';
import { AlertTriangle, MapPin, Table } from 'lucide-react';

interface CivicMapProps {
  issues: Issue[];
  selectedIssue?: Issue | null;
  onSelectIssue?: (issue: Issue) => void;
  pickerMode?: boolean;
  selectedCoordinates?: { lat: number; lng: number } | null;
  onCoordinatesChange?: (coords: { lat: number; lng: number }) => void;
  height?: string;
}

// India metropolitan default center (Bengaluru Central: 12.9716, 77.5946)
const INDIA_DEFAULT_CENTER: L.LatLngTuple = [12.9716, 77.5946];

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
  const issueMarkersMapRef = useRef<Record<number, L.Marker>>({});
  const onCoordsChangeRef = useRef(onCoordinatesChange);
  onCoordsChangeRef.current = onCoordinatesChange;

  const [mapError, setMapError] = useState(false);
  const [showTableFallback, setShowTableFallback] = useState(false);

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    try {
      const initialCenter: L.LatLngTuple = selectedCoordinates && selectedCoordinates.lat && selectedCoordinates.lng
        ? [selectedCoordinates.lat, selectedCoordinates.lng]
        : issues.length > 0 && issues[0].latitude && issues[0].longitude
        ? [issues[0].latitude, issues[0].longitude]
        : INDIA_DEFAULT_CENTER;

      const map = L.map(mapContainerRef.current, {
        center: initialCenter,
        zoom: pickerMode ? 14 : 13,
      });

      // OpenStreetMap Standard Tiles
      const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors | CivicPulse India',
        maxZoom: 19,
      });

      tileLayer.on('tileerror', () => {
        setMapError(true);
      });

      tileLayer.addTo(map);

      const markersLayer = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
      markersLayerRef.current = markersLayer;

      // Ensure proper container sizing after mount
      setTimeout(() => {
        map.invalidateSize();
      }, 200);

      // Picker Mode: Create interactive pin marker immediately
      if (pickerMode) {
        const pickerCoords: L.LatLngTuple = selectedCoordinates
          ? [selectedCoordinates.lat, selectedCoordinates.lng]
          : initialCenter;

        const pickerIcon = L.divIcon({
          className: 'civic-picker-pin-wrapper',
          html: `<div style="
            background: linear-gradient(135deg, #0d9488, #0f766e);
            color: #ffffff;
            border-radius: 50% 50% 50% 0;
            transform: rotate(-45deg);
            width: 34px;
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.4);
            border: 2.5px solid #ffffff;
            cursor: pointer;
          ">
            <span style="transform: rotate(45deg); font-size: 15px; font-weight: 900;">📍</span>
          </div>`,
          iconSize: [34, 34],
          iconAnchor: [17, 34],
        });

        const pMarker = L.marker(pickerCoords, {
          icon: pickerIcon,
          draggable: true,
          autoPan: true,
        }).addTo(map);

        pickerMarkerRef.current = pMarker;

        pMarker.on('dragend', () => {
          const pos = pMarker.getLatLng();
          const updated = {
            lat: Number(pos.lat.toFixed(5)),
            lng: Number(pos.lng.toFixed(5)),
          };
          if (onCoordsChangeRef.current) {
            onCoordsChangeRef.current(updated);
          }
        });

        // Click on map moves pin immediately
        map.on('click', (e: L.LeafletMouseEvent) => {
          const clickedCoords = {
            lat: Number(e.latlng.lat.toFixed(5)),
            lng: Number(e.latlng.lng.toFixed(5)),
          };
          pMarker.setLatLng(e.latlng);
          map.panTo(e.latlng);
          if (onCoordsChangeRef.current) {
            onCoordsChangeRef.current(clickedCoords);
          }
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

  // Sync external coordinate changes (e.g. manual typing in input boxes)
  useEffect(() => {
    if (!mapInstanceRef.current || !pickerMode || !pickerMarkerRef.current) return;
    if (selectedCoordinates && selectedCoordinates.lat && selectedCoordinates.lng) {
      const currentPos = pickerMarkerRef.current.getLatLng();
      const dist = Math.abs(currentPos.lat - selectedCoordinates.lat) + Math.abs(currentPos.lng - selectedCoordinates.lng);
      if (dist > 0.0001) {
        pickerMarkerRef.current.setLatLng([selectedCoordinates.lat, selectedCoordinates.lng]);
        mapInstanceRef.current.panTo([selectedCoordinates.lat, selectedCoordinates.lng]);
      }
    }
  }, [selectedCoordinates, pickerMode]);

  // Invalidate map size on layout/tab changes
  useEffect(() => {
    if (mapInstanceRef.current) {
      const timer = setTimeout(() => {
        mapInstanceRef.current?.invalidateSize();
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [height]);

  // Update and render Issue Markers on Dashboard
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current || pickerMode) return;

    markersLayerRef.current.clearLayers();
    issueMarkersMapRef.current = {};

    issues.forEach((issue) => {
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
        html: `<div style="background-color: ${pinColor}; color: white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 3px 6px rgba(0,0,0,0.35); border: 2px solid white; font-size: 11px; font-weight: bold;">
          ${issue.priority_score ? Math.round(issue.priority_score) : '!'}
        </div>`,
        iconSize: [28, 28],
        iconAnchor: [14, 28],
        popupAnchor: [0, -26],
      });

      const marker = L.marker([issue.latitude, issue.longitude], { icon: customIcon });

      const popupHtml = `
        <div style="font-family: system-ui, -apple-system, sans-serif; min-width: 200px; padding: 2px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 11px; font-weight: 700; color: #0f766e; font-family: monospace;">${issue.public_reference}</span>
            <span style="font-size: 10px; background: #f1f5f9; color: #334155; padding: 2px 7px; border-radius: 9999px; font-weight: 700;">${issue.status}</span>
          </div>
          <div style="font-weight: 700; font-size: 13px; color: #0f172a; margin-bottom: 4px; line-height: 1.3;">${issue.title}</div>
          <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">📍 ${issue.ward_or_district || 'Zone'} - ${issue.approximate_address || ''}</div>
          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; font-weight: 700; border-top: 1px solid #e2e8f0; pt-1; margin-top: 4px;">
            <span style="color: ${pinColor}">Score: ${Math.round(issue.priority_score)}</span>
            <span style="color: #0d9488;">${issue.category?.name || 'Defect'}</span>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml);

      marker.on('click', () => {
        if (onSelectIssue) onSelectIssue(issue);
      });

      markersLayerRef.current?.addLayer(marker);
      issueMarkersMapRef.current[issue.id] = marker;
    });
  }, [issues, pickerMode]);

  // AUTO-MOVE MAP TO REPORT LOCATION WHEN A REPORT IS CLICKED
  useEffect(() => {
    if (!mapInstanceRef.current || !selectedIssue) return;

    const lat = selectedIssue.latitude;
    const lng = selectedIssue.longitude;

    if (lat && lng) {
      mapInstanceRef.current.flyTo([lat, lng], 16, {
        duration: 1.0,
      });

      // Open the marker's popup
      const targetMarker = issueMarkersMapRef.current[selectedIssue.id];
      if (targetMarker) {
        setTimeout(() => {
          targetMarker.openPopup();
        }, 400);
      }
    }
  }, [selectedIssue]);

  return (
    <div className="relative w-full rounded-xl overflow-hidden border border-slate-200 shadow-sm bg-white">
      {/* Map Header Toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-slate-50 border-b border-slate-200 text-xs text-slate-600">
        <div className="flex items-center gap-2 font-medium">
          <MapPin className="w-4 h-4 text-teal-600" />
          <span>
            {pickerMode
              ? 'Click anywhere on map to position pin (or drag marker)'
              : `Civic Operations Map (${issues.length} defect reports plotted)`}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setShowTableFallback(!showTableFallback)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 transition text-[11px] font-semibold"
          >
            <Table className="w-3.5 h-3.5" />
            <span>{showTableFallback ? 'Show Interactive Map' : 'Table View'}</span>
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

      {/* Tabular Fallback or Interactive Leaflet Map */}
      {showTableFallback || mapError ? (
        <div className="overflow-x-auto p-4 max-h-[480px]">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-100 text-slate-800 font-semibold uppercase tracking-wider text-[11px]">
              <tr>
                <th className="p-2.5">Reference</th>
                <th className="p-2.5">Category</th>
                <th className="p-2.5">Title</th>
                <th className="p-2.5">Ward / District Area</th>
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
                      Locate
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div ref={mapContainerRef} style={{ height, width: '100%', minHeight: '260px' }} />
      )}
    </div>
  );
};
