import React, { useState } from 'react';
import { Issue } from '../types';
import { api } from '../api/client';
import { Search, CheckCircle, Clock, MapPin, AlertCircle, FileText, ArrowRight } from 'lucide-react';

interface TrackIssuePageProps {
  initialReference?: string;
}

export const TrackIssuePage: React.FC<TrackIssuePageProps> = ({ initialReference = '' }) => {
  const [reference, setReference] = useState(initialReference);
  const [issue, setIssue] = useState<Issue | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reference.trim()) return;
    setLoading(true);
    setError(null);
    setIssue(null);

    try {
      const data = await api.trackIssue(reference.trim());
      setIssue(data);
    } catch (err: any) {
      setError(err.message || 'Issue not found. Please verify the reference number.');
    } finally {
      setLoading(false);
    }
  };

  const steps = ['Submitted', 'Triaged', 'Assigned', 'In Progress', 'Resolved', 'Verified'];
  const currentStepIdx = issue ? steps.indexOf(issue.status) : -1;

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div className="text-center max-w-xl mx-auto">
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Track Issue Resolution Status</h1>
        <p className="text-xs text-slate-600 mt-1">
          Enter your reference number to monitor work order milestones, triage status, and completion times.
        </p>

        <form onSubmit={handleSearch} className="mt-6 flex gap-2">
          <input
            type="text"
            required
            value={reference}
            onChange={(e) => setReference(e.target.value.toUpperCase())}
            placeholder="e.g. CP-2026-AB12"
            className="flex-1 px-4 py-3 rounded-xl border border-slate-300 font-mono text-sm uppercase tracking-wider focus:outline-none focus:ring-2 focus:ring-teal-500 shadow-sm"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-teal-600 text-white font-bold text-sm hover:bg-teal-700 disabled:opacity-50 transition shadow-sm flex items-center gap-1.5"
          >
            <Search className="w-4 h-4" />
            <span>Search</span>
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-rose-800 text-xs text-center max-w-md mx-auto">
          {error}
        </div>
      )}

      {issue && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-8 animate-fadeIn">
          {/* Header Card */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded border border-teal-200">
                  {issue.public_reference}
                </span>
                <span className="text-xs text-slate-400">&bull;</span>
                <span className="text-xs text-slate-500 font-medium">{issue.category?.name}</span>
              </div>
              <h2 className="text-lg font-bold text-slate-900 mt-1">{issue.title}</h2>
              <div className="text-xs text-slate-500 mt-0.5 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>{issue.approximate_address} ({issue.ward_or_district})</span>
              </div>
            </div>

            <div className="text-right">
              <span className="inline-block px-3 py-1 rounded-full text-xs font-bold bg-teal-100 text-teal-800">
                {issue.status}
              </span>
            </div>
          </div>

          {/* Workflow Stepper */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Resolution Progress</h3>
            <div className="grid grid-cols-2 sm:grid-cols-6 gap-2">
              {steps.map((st, idx) => {
                const isPassed = currentStepIdx >= idx;
                const isCurrent = currentStepIdx === idx;
                return (
                  <div
                    key={st}
                    className={`p-3 rounded-xl border text-center transition ${
                      isCurrent
                        ? 'border-teal-500 bg-teal-50 text-teal-900 font-bold ring-2 ring-teal-500'
                        : isPassed
                        ? 'border-emerald-200 bg-emerald-50 text-emerald-800 font-semibold'
                        : 'border-slate-100 bg-slate-50 text-slate-400'
                    }`}
                  >
                    <div className="text-[10px] uppercase font-bold text-slate-400 mb-1">Step {idx + 1}</div>
                    <div className="text-xs">{st}</div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Status History */}
          {issue.history && issue.history.length > 0 && (
            <div className="pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">Audit Log Updates</h3>
              <div className="space-y-2">
                {issue.history.map((h) => (
                  <div key={h.id} className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                    <div className="flex justify-between items-center text-slate-800 font-semibold">
                      <span>Status changed to: {h.new_status}</span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        {new Date(h.created_at).toLocaleString()}
                      </span>
                    </div>
                    {h.note && <div className="text-slate-600 mt-1 text-[11px]">{h.note}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
