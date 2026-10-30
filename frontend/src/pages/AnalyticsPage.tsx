import React, { useState, useEffect } from 'react';
import { AnalyticsSummary, Hotspot } from '../types';
import { api } from '../api/client';
import {
  BarChart3,
  Clock,
  MapPin,
  Flame,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  PieChart,
} from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumData, hotData] = await Promise.all([
          api.getAnalyticsSummary(),
          api.getHotspots(),
        ]);
        setSummary(sumData);
        setHotspots(hotData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-12 text-center text-xs text-slate-500">Loading civic analytics metrics...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-teal-600" />
          Service-Level Agreement (SLA) & Performance Analytics
        </h1>
        <p className="text-xs text-slate-600 mt-0.5">
          Resolution efficiency, category distribution, average response times, and municipal SLA compliance metrics.
        </p>
      </div>

      {/* SLA Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center flex-shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase text-slate-400">Avg Time to Acknowledge</div>
            <div className="text-2xl font-black text-slate-900 mt-0.5">
              {summary?.avg_acknowledge_hours || 0} <span className="text-sm font-normal text-slate-500">hrs</span>
            </div>
            <div className="text-[11px] text-teal-700 font-medium">Target: &le; 24 hrs</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-sky-50 text-sky-700 flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase text-slate-400">Avg Time to Resolve</div>
            <div className="text-2xl font-black text-slate-900 mt-0.5">
              {summary?.avg_resolve_hours || 0} <span className="text-sm font-normal text-slate-500">hrs</span>
            </div>
            <div className="text-[11px] text-sky-700 font-medium">Target: &le; 72 hrs</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-rose-50 text-rose-700 flex items-center justify-center flex-shrink-0">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase text-slate-400">Overdue Reports</div>
            <div className="text-2xl font-black text-rose-600 mt-0.5">
              {summary?.overdue_issues || 0}
            </div>
            <div className="text-[11px] text-slate-500">Exceeded SLA target deadline</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <div className="text-xs font-bold uppercase text-slate-400">Active Clusters</div>
            <div className="text-2xl font-black text-amber-600 mt-0.5">
              {summary?.active_clusters || 0}
            </div>
            <div className="text-[11px] text-slate-500">Repeated complaints grouped</div>
          </div>
        </div>
      </div>

      {/* Category Breakdown & Status Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Category Breakdown */}
        <div className="lg:col-span-7 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-teal-600" />
              <h2 className="text-sm font-bold text-slate-900">Issues by Infrastructure Category</h2>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">Volume Distribution</span>
          </div>

          <div className="space-y-3 pt-2">
            {summary?.category_breakdown.map((item) => {
              const total = summary.total_issues || 1;
              const pct = Math.round((item.count / total) * 100);
              return (
                <div key={item.category} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold text-slate-800">{item.category}</span>
                    <span className="text-slate-500 font-mono">
                      {item.count} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className="bg-teal-500 h-2 rounded-full"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* SLA Compliance Status Distribution */}
        <div className="lg:col-span-5 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-teal-600" />
              <h2 className="text-sm font-bold text-slate-900">SLA Lifecycle Breakdown</h2>
            </div>
            <span className="text-[11px] text-slate-400 font-mono">Current Status</span>
          </div>

          <div className="space-y-3 pt-2">
            {Object.entries(summary?.status_breakdown || {}).map(([st, cnt]) => {
              const total = summary?.total_issues || 1;
              const pct = Math.round((cnt / total) * 100);
              return (
                <div key={st} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="font-semibold text-slate-800">{st}</span>
                    <span className="text-slate-500 font-mono">
                      {cnt} ({pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        st === 'Resolved' || st === 'Verified'
                          ? 'bg-emerald-500'
                          : st === 'In Progress' || st === 'Assigned'
                          ? 'bg-sky-500'
                          : 'bg-amber-500'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
