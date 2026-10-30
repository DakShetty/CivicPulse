import React, { useState, useEffect } from 'react';
import { Issue } from '../types';
import { api } from '../api/client';
import {
  HardHat,
  CheckCircle,
  Play,
  Clock,
  MapPin,
  Calendar,
  AlertCircle,
  MessageSquare,
} from 'lucide-react';

interface FieldWorkerPageProps {
  issues: Issue[];
  onRefresh: () => void;
}

export const FieldWorkerPage: React.FC<FieldWorkerPageProps> = ({ issues, onRefresh }) => {
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [actionNote, setActionNote] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (issues.length === 0) {
      onRefresh();
    }
  }, []);

  // Filter issues assigned or relevant for field operations
  const assignedIssues = issues.filter(
    (i) => i.status === 'Assigned' || i.status === 'In Progress' || i.assigned_worker
  );

  const handleUpdateStatus = async (issueId: number, newStatus: string) => {
    setLoading(true);
    try {
      await api.updateStatus(issueId, newStatus, actionNote || `Field worker marked ${newStatus}`);
      setActionNote('');
      onRefresh();
      // refresh selected issue
      const updated = await api.getIssue(issueId);
      setSelectedIssue(updated);
    } catch (err: any) {
      alert(err.message || 'Status update failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <HardHat className="w-6 h-6 text-amber-500" />
            Field Worker Operations Console
          </h1>
          <p className="text-xs text-slate-600 mt-1">
            Assigned municipal work orders, progress updates, and resolution logging.
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="px-3.5 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50"
        >
          Refresh Roster
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Left Column: Assigned Orders List (5 cols) */}
        <div className="md:col-span-5 bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
          <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center text-xs">
            <span className="font-bold text-slate-700">My Assigned Tasks ({assignedIssues.length})</span>
            <span className="text-slate-400 font-mono">Active Roster</span>
          </div>

          <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
            {assignedIssues.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No active work orders currently assigned.</div>
            ) : (
              assignedIssues.map((issue) => (
                <div
                  key={issue.id}
                  onClick={() => setSelectedIssue(issue)}
                  className={`p-4 cursor-pointer text-left transition ${
                    selectedIssue?.id === issue.id ? 'bg-amber-50/70 border-l-4 border-amber-500' : 'hover:bg-slate-50'
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[11px] font-bold text-slate-500">{issue.public_reference}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        issue.status === 'In Progress'
                          ? 'bg-amber-100 text-amber-900'
                          : issue.status === 'Resolved'
                          ? 'bg-emerald-100 text-emerald-900'
                          : 'bg-slate-100 text-slate-800'
                      }`}
                    >
                      {issue.status}
                    </span>
                  </div>
                  <h4 className="font-bold text-xs text-slate-900 mt-1 line-clamp-1">{issue.title}</h4>
                  <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-slate-400" />
                    <span>{issue.ward_or_district}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right Column: Work Order Details & Status Actions (7 cols) */}
        <div className="md:col-span-7">
          {selectedIssue ? (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-6">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">
                    {selectedIssue.public_reference}
                  </span>
                  <span className="px-2 py-0.5 rounded text-xs font-bold bg-slate-100 text-slate-800">
                    {selectedIssue.status}
                  </span>
                </div>
                <h3 className="text-lg font-bold text-slate-900 mt-2">{selectedIssue.title}</h3>
                <div className="text-xs text-slate-500 mt-1 flex items-center gap-2">
                  <span>Location: {selectedIssue.approximate_address} ({selectedIssue.ward_or_district})</span>
                </div>
              </div>

              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Defect Description
                </span>
                <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200 leading-relaxed">
                  {selectedIssue.description}
                </p>
              </div>

              {/* Action Form */}
              <div className="pt-4 border-t border-slate-100 space-y-4">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                  Post Progress Update / Transition
                </span>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Field Notes</label>
                  <textarea
                    rows={2}
                    value={actionNote}
                    onChange={(e) => setActionNote(e.target.value)}
                    placeholder="e.g. Cleared debris, gravel base laid down; setting asphalt..."
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-1 focus:ring-amber-500"
                  />
                </div>

                <div className="flex flex-wrap gap-3">
                  <button
                    type="button"
                    disabled={loading || selectedIssue.status === 'In Progress'}
                    onClick={() => handleUpdateStatus(selectedIssue.id, 'In Progress')}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs hover:bg-amber-600 disabled:opacity-50 transition"
                  >
                    <Play className="w-3.5 h-3.5" />
                    Mark In Progress
                  </button>

                  <button
                    type="button"
                    disabled={loading || selectedIssue.status === 'Resolved'}
                    onClick={() => handleUpdateStatus(selectedIssue.id, 'Resolved')}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold text-xs hover:bg-emerald-700 disabled:opacity-50 transition shadow-sm"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    Mark Work Completed (Resolved)
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 text-xs">
              Select an assigned work order from the left to view details and post field progress updates.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
