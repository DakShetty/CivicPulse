import React, { useState, useEffect } from 'react';
import { Issue, IssueCategory, User } from '../types';
import { CivicMap } from '../components/CivicMap';
import { api } from '../api/client';
import {
  AlertTriangle,
  Clock,
  CheckCircle,
  FolderGit2,
  Filter,
  Search,
  Eye,
  UserCheck,
  Calendar,
  Flame,
  ArrowRight,
  Shield,
  Layers,
} from 'lucide-react';

interface DashboardPageProps {
  issues: Issue[];
  categories: IssueCategory[];
  currentUser: User | null;
  onRefresh: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  issues,
  categories,
  currentUser,
  onRefresh,
}) => {
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedStatusNote, setSelectedStatusNote] = useState<string>('');
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);

  useEffect(() => {
    if (issues.length === 0) {
      onRefresh();
    }
  }, []);

  // Filter issues
  const filteredIssues = issues.filter((i) => {
    if (categoryFilter && String(i.category?.id) !== categoryFilter) return false;
    if (statusFilter && i.status !== statusFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchTitle = i.title.toLowerCase().includes(q);
      const matchRef = i.public_reference.toLowerCase().includes(q);
      const matchWard = (i.ward_or_district || '').toLowerCase().includes(q);
      if (!matchTitle && !matchRef && !matchWard) return false;
    }
    return true;
  });

  // KPI Calculations
  const totalCount = issues.length;
  const resolvedCount = issues.filter((i) => i.status === 'Resolved' || i.status === 'Verified').length;
  const openCount = totalCount - resolvedCount - issues.filter((i) => i.status === 'Rejected').length;
  const criticalCount = issues.filter((i) => i.safety_hazard || i.priority_score >= 70).length;
  const clusterCount = issues.filter((i) => i.cluster_id !== null).length;

  const handleStatusChange = async (newStatus: string) => {
    if (!selectedIssue) return;
    setIsUpdatingStatus(true);
    try {
      await api.updateStatus(selectedIssue.id, newStatus, selectedStatusNote || `Status changed to ${newStatus}`);
      setSelectedStatusNote('');
      // Refresh single issue view
      const updated = await api.getIssue(selectedIssue.id);
      setSelectedIssue(updated);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Top Header & Context */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            Civic Operations Intelligence Hub
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Geospatial issue triage, SLA tracking, and priority score escalation across municipal zones.
          </p>
        </div>
        <button
          onClick={onRefresh}
          className="self-start md:self-auto px-3.5 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-50 shadow-sm"
        >
          Refresh Data
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">Total Reports</div>
          <div className="text-2xl font-black text-slate-900 mt-1">{totalCount}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">All community submissions</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-[11px] font-bold uppercase tracking-wider text-amber-600">Active / Open</div>
          <div className="text-2xl font-black text-amber-600 mt-1">{openCount}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Under triage or in progress</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-[11px] font-bold uppercase tracking-wider text-rose-600">High Risk / Safety</div>
          <div className="text-2xl font-black text-rose-600 mt-1">{criticalCount}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Priority score &gt; 70 or hazard</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-[11px] font-bold uppercase tracking-wider text-teal-600">Clustered Duplicates</div>
          <div className="text-2xl font-black text-teal-600 mt-1">{clusterCount}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Linked reports near each other</div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
          <div className="text-[11px] font-bold uppercase tracking-wider text-emerald-600">Resolved / Closed</div>
          <div className="text-2xl font-black text-emerald-600 mt-1">{resolvedCount}</div>
          <div className="text-[10px] text-slate-400 mt-0.5">Work completed & verified</div>
        </div>
      </div>

      {/* Main Operations Split: Map & Issue Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Interactive Map (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <CivicMap
            issues={filteredIssues}
            selectedIssue={selectedIssue}
            onSelectIssue={(issue) => setSelectedIssue(issue)}
            height="520px"
          />

          <div className="flex items-center justify-between text-xs text-slate-500 bg-white p-3 rounded-xl border border-slate-200">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-600"></span> High Priority (&gt;70)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> Moderate (45-69)
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Resolved
              </span>
            </div>
            <span className="text-[11px] font-mono">Tile Provider: OpenStreetMap</span>
          </div>
        </div>

        {/* Right Column: Filterable Feed (5 cols) */}
        <div className="lg:col-span-5 flex flex-col space-y-3">
          {/* Filter Bar */}
          <div className="bg-white p-3 rounded-xl border border-slate-200 space-y-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-3" />
              <input
                type="text"
                placeholder="Search by title, ref #, or area..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-teal-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-2">
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700 bg-white"
              >
                <option value="">All Categories</option>
                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs text-slate-700 bg-white"
              >
                <option value="">All Statuses</option>
                <option value="Submitted">Submitted</option>
                <option value="Triaged">Triaged</option>
                <option value="Assigned">Assigned</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
                <option value="Verified">Verified</option>
              </select>
            </div>
          </div>

          {/* List items */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden divide-y divide-slate-100 flex-1 max-h-[460px] overflow-y-auto">
            {filteredIssues.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-400">No issues match current filters.</div>
            ) : (
              filteredIssues.map((issue) => {
                const isSelected = selectedIssue?.id === issue.id;
                return (
                  <div
                    key={issue.id}
                    onClick={() => setSelectedIssue(issue)}
                    className={`p-3.5 cursor-pointer transition text-left ${
                      isSelected ? 'bg-teal-50/70 border-l-4 border-teal-600' : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-[11px] font-bold text-slate-500">
                        {issue.public_reference}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                        {issue.status}
                      </span>
                    </div>

                    <div className="font-bold text-xs text-slate-900 mt-1 line-clamp-1">{issue.title}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5 line-clamp-1">{issue.approximate_address}</div>

                    <div className="flex items-center justify-between mt-2 pt-1.5 border-t border-slate-100/80 text-[11px]">
                      <span className="text-teal-700 font-medium">{issue.category?.name}</span>
                      <span className="font-bold text-slate-800">
                        Priority: <span className="text-teal-600">{Math.round(issue.priority_score)}</span>
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>

      {/* Issue Detail Drawer / Modal */}
      {selectedIssue && (
        <div className="bg-white rounded-2xl border border-slate-200 shadow-lg p-6 space-y-6">
          <div className="flex items-start justify-between border-b border-slate-100 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded border border-teal-200">
                  {selectedIssue.public_reference}
                </span>
                <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-800">
                  {selectedIssue.status}
                </span>
                {selectedIssue.safety_hazard && (
                  <span className="flex items-center gap-1 text-[11px] font-bold text-rose-600 bg-rose-50 px-2 py-0.5 rounded border border-rose-200">
                    <Flame className="w-3 h-3" /> Safety Hazard
                  </span>
                )}
              </div>
              <h2 className="text-lg font-bold text-slate-900 mt-2">{selectedIssue.title}</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                {selectedIssue.ward_or_district} &bull; {selectedIssue.approximate_address}
              </p>
            </div>

            <button
              onClick={() => setSelectedIssue(null)}
              className="text-xs text-slate-400 hover:text-slate-700 px-2 py-1 rounded"
            >
              Close
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left: Description & Explainable Priority */}
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Resident Description</h3>
                <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200 mt-1 leading-relaxed">
                  {selectedIssue.description}
                </p>
              </div>

              {/* Explainable Priority Breakdown */}
              <div className="p-4 rounded-xl bg-slate-900 text-white space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-teal-400 uppercase tracking-wide">
                    Explainable Priority Score
                  </span>
                  <span className="text-xl font-black text-teal-400">{Math.round(selectedIssue.priority_score)}/100</span>
                </div>
                <div className="text-[11px] text-slate-300 leading-normal border-t border-slate-800 pt-2 font-mono">
                  {selectedIssue.priority_explanation || 'Standard severity weighting applied.'}
                </div>
              </div>

              {/* Attachments */}
              {selectedIssue.attachments && selectedIssue.attachments.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Photo Evidence</h3>
                  <div className="flex gap-3">
                    {selectedIssue.attachments.map((att) => (
                      <a
                        key={att.id}
                        href={att.download_url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-teal-700 bg-teal-50 hover:bg-teal-100"
                      >
                        <span>View Attachment ({att.original_filename})</span>
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right: Workflow Status Actions & Assignment */}
            <div className="space-y-4 border-t md:border-t-0 md:border-l border-slate-100 md:pl-6">
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Workflow State Transitions
                </h3>
                <div className="flex flex-wrap gap-2">
                  {['Submitted', 'Triaged', 'Assigned', 'In Progress', 'Resolved', 'Verified'].map((st) => (
                    <button
                      key={st}
                      type="button"
                      disabled={isUpdatingStatus || selectedIssue.status === st}
                      onClick={() => handleStatusChange(st)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                        selectedIssue.status === st
                          ? 'bg-teal-600 text-white font-bold ring-2 ring-teal-600 ring-offset-1'
                          : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                      }`}
                    >
                      {st}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 mb-1">
                  Transition Note / Action Summary
                </label>
                <input
                  type="text"
                  value={selectedStatusNote}
                  onChange={(e) => setSelectedStatusNote(e.target.value)}
                  placeholder="e.g. Assigned to crew #3 for asphalt patching"
                  className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs focus:ring-1 focus:ring-teal-500"
                />
              </div>

              {/* Status History Timeline */}
              {selectedIssue.history && selectedIssue.history.length > 0 && (
                <div className="pt-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                    Audit Status History
                  </h3>
                  <div className="space-y-2 max-h-36 overflow-y-auto pr-1">
                    {selectedIssue.history.map((h) => (
                      <div key={h.id} className="text-[11px] p-2 rounded-lg bg-slate-50 border border-slate-100">
                        <div className="flex justify-between font-semibold text-slate-800">
                          <span>{h.new_status}</span>
                          <span className="text-slate-400 font-normal">{h.actor_name}</span>
                        </div>
                        {h.note && <div className="text-slate-600 mt-0.5">{h.note}</div>}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
