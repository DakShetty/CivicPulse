import React, { useState } from 'react';
import { IssueCategory } from '../types';
import { CivicMap } from '../components/CivicMap';
import { api } from '../api/client';
import {
  AlertTriangle,
  Camera,
  CheckCircle2,
  Send,
  MapPin,
  Flame,
  ShieldCheck,
  Building2,
  Copy,
} from 'lucide-react';

interface ReportIssuePageProps {
  categories: IssueCategory[];
  onIssueSubmitted?: () => void;
  onNavigateToTrack?: (ref: string) => void;
}

export const ReportIssuePage: React.FC<ReportIssuePageProps> = ({
  categories,
  onIssueSubmitted,
  onNavigateToTrack,
}) => {
  const [categoryId, setCategoryId] = useState<number | string>(categories[0]?.id || 1);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [ward, setWard] = useState('Central Zone - Ward 111 (Shantala Nagar)');
  const [address, setAddress] = useState('MG Road near Brigade Road Signal, Bengaluru');
  const [coordinates, setCoordinates] = useState<{ lat: number; lng: number }>({
    lat: 12.9752,
    lng: 77.6095,
  });
  const [isLocating, setIsLocating] = useState(false);
  const [severity, setSeverity] = useState(3);
  const [safetyHazard, setSafetyHazard] = useState(false);
  const [impactsCritical, setImpactsCritical] = useState(false);
  const [photoFile, setPhotoFile] = useState<File | null>(null);

  // Regional Indian offline fallback heuristics
  const getOfflineLocation = (lat: number, lng: number) => {
    // Mumbai Region (lat: 18.8 - 19.35, lng: 72.7 - 73.15)
    if (lat >= 18.8 && lat <= 19.35 && lng >= 72.7 && lng <= 73.15) {
      if (lat >= 19.1) {
        return {
          ward: 'BMC Zone IV - Andheri West / Goregaon',
          address: 'Near Link Road & SV Road, Mumbai, Maharashtra',
        };
      } else if (lat >= 19.0) {
        return {
          ward: 'BMC Zone III - Bandra West / Khar',
          address: 'Near Hill Road / Bandra Bandstand, Mumbai, Maharashtra',
        };
      } else {
        return {
          ward: 'BMC Zone I - South Mumbai (Colaba / Marine Drive)',
          address: 'Near Marine Drive Promenade, Mumbai, Maharashtra',
        };
      }
    }
    // Delhi NCR Region (lat: 28.4 - 28.9, lng: 76.9 - 77.45)
    if (lat >= 28.4 && lat <= 28.9 && lng >= 76.9 && lng <= 77.45) {
      if (lat >= 28.6) {
        return {
          ward: 'MCD Central Zone - Connaught Place / Karol Bagh',
          address: 'Near Barakhamba Road, New Delhi, Delhi',
        };
      } else {
        return {
          ward: 'MCD South Zone - Hauz Khas / Saket',
          address: 'Near Outer Ring Road, South Delhi, Delhi',
        };
      }
    }
    // Bengaluru Region (lat: 12.8 - 13.15, lng: 77.45 - 77.8)
    if (lat >= 12.8 && lat <= 13.15 && lng >= 77.45 && lng <= 77.8) {
      if (lng >= 77.63) {
        return {
          ward: 'BBMP East Zone - Indiranagar (Ward 80)',
          address: '100 Feet Road, Near 12th Main, Indiranagar, Bengaluru',
        };
      } else if (lat <= 12.94) {
        return {
          ward: 'BBMP South Zone - Koramangala (Ward 151)',
          address: 'Near Sony World Signal, Koramangala 4th Block, Bengaluru',
        };
      } else {
        return {
          ward: 'BBMP Central Zone - Ward 111 (Shantala Nagar)',
          address: 'MG Road near Brigade Road Signal, Bengaluru',
        };
      }
    }
    // Pune Region (lat: 18.4 - 18.7, lng: 73.7 - 74.0)
    if (lat >= 18.4 && lat <= 18.7 && lng >= 73.7 && lng <= 74.0) {
      return {
        ward: 'PMC Zone 2 - Shivajinagar / Kothrud',
        address: 'FC Road / Karve Road, Pune, Maharashtra',
      };
    }
    // Chennai Region (lat: 12.9 - 13.2, lng: 80.1 - 80.35)
    if (lat >= 12.9 && lat <= 13.2 && lng >= 80.1 && lng <= 80.35) {
      return {
        ward: 'Greater Chennai Corp - Zone 10 (T. Nagar)',
        address: 'Near Usman Road / Panagal Park, Chennai, Tamil Nadu',
      };
    }
    // Hyderabad Region (lat: 17.3 - 17.6, lng: 78.3 - 78.6)
    if (lat >= 17.3 && lat <= 17.6 && lng >= 78.3 && lng <= 78.6) {
      return {
        ward: 'GHMC West Zone - Hitec City / Madhapur (Ward 107)',
        address: 'Near Cyber Towers, Hitec City, Hyderabad, Telangana',
      };
    }
    // Kolkata Region (lat: 22.4 - 22.7, lng: 88.2 - 88.5)
    if (lat >= 22.4 && lat <= 22.7 && lng >= 88.2 && lng <= 88.5) {
      return {
        ward: 'KMC Borough VII - Park Street',
        address: 'Park Street / Camac Street, Kolkata, West Bengal',
      };
    }

    return {
      ward: `Municipal Ward [${lat.toFixed(3)}N, ${lng.toFixed(3)}E]`,
      address: `Near Landmark Coordinates (${lat.toFixed(4)}, ${lng.toFixed(4)}), India`,
    };
  };

  // Dynamic reverse-geocoding handler triggered when user clicks or drags map pin
  const handleMapCoordinatesChange = async (newCoords: { lat: number; lng: number }) => {
    setCoordinates(newCoords);
    setIsLocating(true);

    // 1. Instant offline heuristic update so UI changes in 0ms
    const fallback = getOfflineLocation(newCoords.lat, newCoords.lng);
    setWard(fallback.ward);
    setAddress(fallback.address);

    // 2. Query Nominatim reverse geocoder for pinpoint exact street / district
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${newCoords.lat}&lon=${newCoords.lng}`,
        {
          signal: controller.signal,
          headers: { 'Accept-Language': 'en' },
        }
      );
      clearTimeout(timeoutId);
      if (res.ok) {
        const data = await res.json();
        if (data && data.address) {
          const a = data.address;
          const road = a.road || a.pedestrian || a.suburb || a.neighbourhood || '';
          const neighborhood = a.suburb || a.neighbourhood || a.city_district || a.quarter || '';
          const city = a.city || a.town || a.village || a.state_district || '';
          const state = a.state || 'India';

          const resolvedWard = neighborhood
            ? `${neighborhood} (${city || 'Ward'})`
            : city
            ? `${city} Municipal Zone`
            : fallback.ward;

          const addressParts = [road, neighborhood, city, state].filter(
            (part, index, self) => Boolean(part) && self.indexOf(part) === index
          );
          const resolvedAddress = addressParts.length > 0 ? addressParts.join(', ') : fallback.address;

          setWard(resolvedWard);
          setAddress(resolvedAddress);
        }
      }
    } catch {
      // Retain the immediate offline heuristic
    } finally {
      setIsLocating(false);
    }
  };

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successResult, setSuccessResult] = useState<{
    reference: string;
    duplicate_detected?: any;
    priority_score?: number;
  } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('category_id', String(categoryId));
      formData.append('title', title);
      formData.append('description', description);
      formData.append('ward_or_district', ward);
      formData.append('approximate_address', address);
      formData.append('latitude', String(coordinates.lat));
      formData.append('longitude', String(coordinates.lng));
      formData.append('severity', String(severity));
      formData.append('safety_hazard', String(safetyHazard));
      formData.append('impacts_critical_infrastructure', String(impactsCritical));

      if (photoFile) {
        formData.append('photo', photoFile);
      }

      const res = await api.createIssue(formData);
      setSuccessResult({
        reference: res.public_reference,
        duplicate_detected: res.duplicate_detected,
        priority_score: res.issue.priority_score,
      });

      if (onIssueSubmitted) onIssueSubmitted();
    } catch (err: any) {
      setError(err.message || 'Failed to submit issue report.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Report a Public Infrastructure Issue</h1>
        <p className="text-sm text-slate-600 mt-1">
          Help community maintenance teams triage potholes, broken lights, and water leaks. Do not include personal identity in photos or descriptions.
        </p>
      </div>

      {/* Success Modal / Banner */}
      {successResult ? (
        <div className="bg-white rounded-2xl p-8 border border-teal-200 shadow-xl text-center mb-8">
          <div className="w-16 h-16 bg-teal-100 text-teal-700 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Report Successfully Submitted</h2>
          <p className="text-sm text-slate-600 mt-1">Your civic reference tracking number is:</p>
          
          <div className="inline-flex items-center gap-2 bg-slate-100 px-4 py-2 rounded-lg font-mono text-lg font-bold text-slate-900 my-4 border border-slate-300">
            <span>{successResult.reference}</span>
            <button
              onClick={() => navigator.clipboard.writeText(successResult.reference)}
              className="text-slate-500 hover:text-slate-800"
              title="Copy reference"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>

          {/* Explainable duplicate alert notice */}
          {successResult.duplicate_detected && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-left max-w-lg mx-auto my-4 text-xs text-amber-900">
              <div className="flex items-center gap-2 font-bold mb-1">
                <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span>Existing Infrastructure Cluster Detected!</span>
              </div>
              <p>
                A similar report ({successResult.duplicate_detected.matched_reference}) was already reported nearby. Both reports have been linked in an issue cluster to escalate priority for maintenance crews.
              </p>
              <p className="font-mono mt-1 text-[11px] text-amber-700">
                {successResult.duplicate_detected.explanation}
              </p>
            </div>
          )}

          <div className="flex justify-center gap-3 mt-6">
            <button
              onClick={() => {
                setSuccessResult(null);
                setTitle('');
                setDescription('');
                setPhotoFile(null);
              }}
              className="px-5 py-2.5 rounded-lg bg-teal-600 text-white font-semibold text-sm hover:bg-teal-700 transition"
            >
              Report Another Issue
            </button>
            {onNavigateToTrack && (
              <button
                onClick={() => onNavigateToTrack(successResult.reference)}
                className="px-5 py-2.5 rounded-lg bg-slate-800 text-white font-semibold text-sm hover:bg-slate-900 transition"
              >
                Track Live Status
              </button>
            )}
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-6">
          {error && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Issue Category */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
              Issue Category *
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {categories.map((cat) => (
                <button
                  type="button"
                  key={cat.id}
                  onClick={() => setCategoryId(cat.id)}
                  className={`p-3 rounded-xl border text-left text-xs font-medium transition ${
                    Number(categoryId) === cat.id
                      ? 'border-teal-500 bg-teal-50 text-teal-900 font-bold shadow-sm ring-1 ring-teal-500'
                      : 'border-slate-200 hover:border-slate-300 text-slate-700'
                  }`}
                >
                  <div className="truncate">{cat.name}</div>
                  <div className="text-[10px] text-slate-400 font-normal mt-0.5">SLA: {cat.sla_hours}h</div>
                </button>
              ))}
            </div>
          </div>

          {/* Title & Description */}
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                Summary Title *
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Hazardous deep pothole on right lane"
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                Detailed Description *
              </label>
              <textarea
                required
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe visible damage, traffic disruption, or hazards..."
                className="w-full px-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
              />
            </div>
          </div>

          {/* Location Picker & Ward */}
          <div className="space-y-4 pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block">
                  Location & Map Placement *
                </span>
                <span className="text-[11px] text-slate-500">
                  Click on the map or drag the pin to set the issue coordinates
                </span>
              </div>
              <div className="flex items-center gap-2">
                {isLocating && (
                  <span className="text-[11px] font-semibold text-teal-700 animate-pulse flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-teal-600 animate-ping inline-block"></span>
                    Resolving location...
                  </span>
                )}
                <div className="flex items-center gap-1.5 text-xs font-mono bg-teal-50 px-2 py-1 rounded border border-teal-200">
                  <span className="text-teal-900 font-bold">Lat:</span>
                  <input
                    type="number"
                    step="0.0001"
                    value={coordinates.lat}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value) || coordinates.lat;
                      handleMapCoordinatesChange({ ...coordinates, lat: val });
                    }}
                    className="w-20 bg-white border border-teal-300 rounded px-1.5 py-0.5 text-xs text-slate-800 focus:outline-none"
                  />
                  <span className="text-teal-900 font-bold ml-1">Lng:</span>
                  <input
                    type="number"
                    step="0.0001"
                    value={coordinates.lng}
                    onChange={(e) => {
                      const val = parseFloat(e.target.value) || coordinates.lng;
                      handleMapCoordinatesChange({ ...coordinates, lng: val });
                    }}
                    className="w-20 bg-white border border-teal-300 rounded px-1.5 py-0.5 text-xs text-slate-800 focus:outline-none"
                  />
                </div>
              </div>
            </div>

            <CivicMap
              issues={[]}
              pickerMode={true}
              selectedCoordinates={coordinates}
              onCoordinatesChange={handleMapCoordinatesChange}
              height="260px"
            />

            <div className="flex items-center justify-between text-[11px] text-teal-700 bg-teal-50/70 border border-teal-200/80 px-3 py-1.5 rounded-lg">
              <span className="flex items-center gap-1.5 font-medium">
                <MapPin className="w-3.5 h-3.5 text-teal-600" />
                Location & Ward auto-update dynamically when you click anywhere on the map.
              </span>
              <span className="font-mono text-[10px] text-slate-500">
                {coordinates.lat.toFixed(4)}, {coordinates.lng.toFixed(4)}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Ward / District Area</label>
                <input
                  type="text"
                  value={ward}
                  onChange={(e) => setWard(e.target.value)}
                  placeholder="e.g. Indiranagar, Koramangala, Whitefield"
                  className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Approximate Landmark / Street</label>
                <input
                  type="text"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="e.g. Near Metro Station / Sony World Signal"
                  className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500"
                />
              </div>
            </div>
          </div>

          {/* Severity & Safety Impact */}
          <div className="pt-2 border-t border-slate-100 space-y-4">
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-700">
                  Reported Severity (Level {severity}/5)
                </label>
                <span className="text-xs font-semibold text-amber-700">
                  {severity === 5 ? 'Critical Danger' : severity >= 4 ? 'High Disruption' : severity >= 3 ? 'Moderate' : 'Low / Cosmetic'}
                </span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={severity}
                onChange={(e) => setSeverity(Number(e.target.value))}
                className="w-full accent-teal-600 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-slate-400">
                <span>1 - Minor defect</span>
                <span>3 - Noticeable</span>
                <span>5 - Complete road blockage / Danger</span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <label className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition ${
                safetyHazard ? 'border-rose-400 bg-rose-50/60' : 'border-slate-200 hover:border-slate-300'
              }`}>
                <input
                  type="checkbox"
                  checked={safetyHazard}
                  onChange={(e) => setSafetyHazard(e.target.checked)}
                  className="rounded text-rose-600 focus:ring-rose-500 h-4 w-4"
                />
                <div className="text-xs">
                  <div className="font-bold text-slate-900 flex items-center gap-1.5">
                    <Flame className="w-3.5 h-3.5 text-rose-600" />
                    Direct Safety Hazard
                  </div>
                  <div className="text-slate-500 text-[11px]">Poses imminent risk of injury or vehicle accident</div>
                </div>
              </label>

              <label className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition ${
                impactsCritical ? 'border-sky-400 bg-sky-50/60' : 'border-slate-200 hover:border-slate-300'
              }`}>
                <input
                  type="checkbox"
                  checked={impactsCritical}
                  onChange={(e) => setImpactsCritical(e.target.checked)}
                  className="rounded text-sky-600 focus:ring-sky-500 h-4 w-4"
                />
                <div className="text-xs">
                  <div className="font-bold text-slate-900 flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-sky-600" />
                    Critical Public Transit / Hospital Route
                  </div>
                  <div className="text-slate-500 text-[11px]">Blocks major transit route or emergency utility</div>
                </div>
              </label>
            </div>
          </div>

          {/* Photo Attachment */}
          <div className="pt-2 border-t border-slate-100">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
              Attach Issue Photo (Optional)
            </label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-slate-300 text-xs font-medium text-slate-700 hover:bg-slate-50 cursor-pointer transition">
                <Camera className="w-4 h-4 text-teal-600" />
                <span>{photoFile ? photoFile.name : 'Select JPG, PNG or WebP (max 8MB)'}</span>
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setPhotoFile(e.target.files[0]);
                    }
                  }}
                />
              </label>
              {photoFile && (
                <button
                  type="button"
                  onClick={() => setPhotoFile(null)}
                  className="text-xs text-rose-600 hover:underline"
                >
                  Remove
                </button>
              )}
            </div>
          </div>

          {/* Submit Action */}
          <div className="pt-4 border-t border-slate-100 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-teal-600 text-white font-bold text-sm shadow-md hover:bg-teal-700 disabled:opacity-50 transition"
            >
              {loading ? (
                <span>Submitting report...</span>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  <span>Submit Public Report</span>
                </>
              )}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
