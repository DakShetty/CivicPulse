import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { User } from '../types';
import {
  HardHat,
  UserCheck,
  UserX,
  Clock,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  PlusCircle,
  Mail,
  Lock,
} from 'lucide-react';

export const WorkerApprovalsPage: React.FC = () => {
  const [pendingWorkers, setPendingWorkers] = useState<User[]>([]);
  const [allWorkers, setAllWorkers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Admin provision new admin form state
  const [showAdminForm, setShowAdminForm] = useState(false);
  const [adminName, setAdminName] = useState('');
  const [adminEmail, setAdminEmail] = useState('');
  const [adminPass, setAdminPass] = useState('');
  const [adminCreating, setAdminCreating] = useState(false);

  const fetchWorkers = async () => {
    setLoading(true);
    try {
      const [pending, all] = await Promise.all([
        api.getPendingWorkers(),
        api.getAllWorkers(),
      ]);
      setPendingWorkers(pending);
      setAllWorkers(all);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkers();
  }, []);

  const handleApprove = async (userId: number) => {
    setActionLoading(userId);
    setFeedback(null);
    try {
      const res = await api.approveWorker(userId);
      setFeedback({ type: 'success', message: res.message });
      await fetchWorkers();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Approval failed' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (userId: number) => {
    if (!window.confirm('Are you sure you want to reject this worker registration?')) return;
    setActionLoading(userId);
    setFeedback(null);
    try {
      const res = await api.rejectWorker(userId);
      setFeedback({ type: 'success', message: res.message });
      await fetchWorkers();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Rejection failed' });
    } finally {
      setActionLoading(null);
    }
  };

  const handleCreateAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAdminCreating(true);
    setFeedback(null);
    try {
      const res = await api.createAdminUser(adminName, adminEmail, adminPass);
      setFeedback({ type: 'success', message: res.message });
      setAdminName('');
      setAdminEmail('');
      setAdminPass('');
      setShowAdminForm(false);
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to create admin' });
    } finally {
      setAdminCreating(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <HardHat className="w-6 h-6 text-amber-600" />
            Worker Approvals & Role Administration
          </h1>
          <p className="text-xs text-slate-600 mt-1">
            Review self-registered field workers requiring verification and provision administrator accounts.
          </p>
        </div>

        <button
          onClick={() => setShowAdminForm(!showAdminForm)}
          className="self-start sm:self-auto flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 transition"
        >
          <PlusCircle className="w-4 h-4 text-teal-400" />
          <span>{showAdminForm ? 'Close Admin Form' : 'Provision New Admin'}</span>
        </button>
      </div>

      {feedback && (
        <div
          className={`p-3.5 rounded-xl border text-xs flex items-center gap-2 ${
            feedback.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
              : 'bg-rose-50 border-rose-200 text-rose-900'
          }`}
        >
          {feedback.type === 'success' ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
          )}
          <span>{feedback.message}</span>
        </div>
      )}

      {/* Provision New Admin Form */}
      {showAdminForm && (
        <form
          onSubmit={handleCreateAdmin}
          className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-4"
        >
          <div className="border-b border-slate-100 pb-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-teal-600" />
              Secure Administrator Account Provisioning
            </h3>
            <p className="text-[11px] text-slate-500">
              Only authorized existing administrators can create admin credentials.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Display Name</label>
              <input
                type="text"
                required
                value={adminName}
                onChange={(e) => setAdminName(e.target.value)}
                placeholder="e.g. Chief Ops Admin"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={adminEmail}
                onChange={(e) => setAdminEmail(e.target.value)}
                placeholder="admin@civicpulse.org"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Password</label>
              <input
                type="password"
                required
                minLength={6}
                value={adminPass}
                onChange={(e) => setAdminPass(e.target.value)}
                placeholder="••••••••"
                className="w-full px-3 py-2 rounded-lg border border-slate-300 text-xs focus:ring-2 focus:ring-teal-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={adminCreating}
              className="px-4 py-2 rounded-lg bg-teal-600 text-white font-bold text-xs hover:bg-teal-700 disabled:opacity-50 transition"
            >
              {adminCreating ? 'Creating Admin...' : 'Confirm & Create Admin Account'}
            </button>
          </div>
        </form>
      )}

      {/* Pending Worker Approvals */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-amber-50/60 border-b border-amber-200 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-amber-700" />
            <h2 className="text-sm font-bold text-slate-900">
              Pending Field Worker Registrations ({pendingWorkers.length})
            </h2>
          </div>
          <span className="text-[11px] text-amber-800 font-semibold bg-amber-100 px-2.5 py-0.5 rounded-full">
            Requires Admin Action
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading worker records...</div>
        ) : pendingWorkers.length === 0 ? (
          <div className="p-8 text-center text-xs text-slate-500">
            No field workers are currently awaiting approval. All worker registrations are verified.
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {pendingWorkers.map((worker) => (
              <div
                key={worker.id}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50"
              >
                <div>
                  <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
                    <span>{worker.display_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-amber-100 text-amber-800 font-semibold">
                      Pending Approval
                    </span>
                  </div>
                  <div className="text-xs text-slate-500 font-mono mt-0.5">{worker.email}</div>
                  <div className="text-[10px] text-slate-400 mt-1">
                    Registered: {worker.created_at ? new Date(worker.created_at).toLocaleString() : 'Recently'}
                  </div>
                </div>

                <div className="flex items-center gap-2 self-start sm:self-auto">
                  <button
                    onClick={() => handleApprove(worker.id)}
                    disabled={actionLoading === worker.id}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-teal-600 text-white font-semibold text-xs hover:bg-teal-700 disabled:opacity-50 shadow-sm transition"
                  >
                    <UserCheck className="w-3.5 h-3.5" />
                    <span>Approve Worker</span>
                  </button>
                  <button
                    onClick={() => handleReject(worker.id)}
                    disabled={actionLoading === worker.id}
                    className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-rose-200 text-rose-700 hover:bg-rose-50 font-semibold text-xs disabled:opacity-50 transition"
                  >
                    <UserX className="w-3.5 h-3.5" />
                    <span>Reject</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* All Registered Workers List */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900">
            All Field Worker Accounts ({allWorkers.length})
          </h2>
          <span className="text-[11px] text-slate-400 font-mono">Municipal Staff Roster</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="p-3">Worker Name</th>
                <th className="p-3">Email Address</th>
                <th className="p-3">Status</th>
                <th className="p-3">Joined Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {allWorkers.map((w) => (
                <tr key={w.id} className="hover:bg-slate-50">
                  <td className="p-3 font-bold text-slate-900">{w.display_name}</td>
                  <td className="p-3 text-slate-600 font-mono">{w.email}</td>
                  <td className="p-3">
                    {w.is_active ? (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-800">
                        Active / Approved
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-800">
                        Pending Admin Approval
                      </span>
                    )}
                  </td>
                  <td className="p-3 text-slate-400">
                    {w.created_at ? new Date(w.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
