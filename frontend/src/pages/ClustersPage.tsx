import React, { useState, useEffect } from 'react';
import { IssueCluster } from '../types';
import { api } from '../api/client';
import {
  GitMerge,
  CheckCircle,
  XCircle,
  Split,
  AlertCircle,
  HelpCircle,
  ExternalLink,
  ShieldCheck,
} from 'lucide-react';

export const ClustersPage: React.FC = () => {
  const [clusters, setClusters] = useState<IssueCluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewingId, setReviewingId] = useState<number | null>(null);

  const fetchClusters = async () => {
    setLoading(true);
    try {
      const data = await api.getClusters();
      setClusters(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClusters();
  }, []);

  const handleReviewAction = async (
    memberId: number,
    action: 'confirmed' | 'separated' | 'dismissed'
  ) => {
    setReviewingId(memberId);
    try {
      await api.reviewClusterMember(memberId, action, `Admin reviewed suggestion as ${action}`);
      await fetchClusters();
    } catch (err: any) {
      alert(err.message || 'Review action failed');
    } finally {
      setReviewingId(null);
    }
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      {/* Header & Explainability Disclaimer */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <GitMerge className="w-6 h-6 text-teal-600" />
          Duplicate-Report Clustering & Deduplication Engine
        </h1>
        <p className="text-xs text-slate-600 mt-1">
          Identifies reports of the same physical defect using geospatial distance threshold (&le; 350m) and Jaccard text overlap.
        </p>
      </div>

      {/* Transparent Logic Architecture Notice */}
      <div className="p-4 rounded-xl bg-teal-50 border border-teal-200 text-teal-950 text-xs space-y-1.5">
        <div className="font-bold flex items-center gap-1.5 text-teal-900">
          <ShieldCheck className="w-4 h-4 text-teal-700" />
          Explainable Clustering Policy (Specification Section 4.3 Compliance)
        </div>
        <p className="leading-relaxed text-teal-800">
          CivicPulse never silently merges or deletes similar reports. Each submission remains an independent legal record with its own timestamps and citizen reference. Admins review AI/rule suggestions to confirm grouped work orders or separate them.
        </p>
      </div>

      {/* Cluster List */}
      {loading ? (
        <div className="p-12 text-center text-xs text-slate-500">Loading duplicate cluster suggestions...</div>
      ) : clusters.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center text-slate-400 text-sm">
          No duplicate clusters detected. All current reports are geographically distinct.
        </div>
      ) : (
        <div className="space-y-4">
          {clusters.map((cluster) => (
            <div key={cluster.id} className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
                <div>
                  <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500">
                    Cluster ID #{cluster.id}
                  </span>
                  <h3 className="text-sm font-bold text-slate-900">{cluster.title}</h3>
                </div>
                <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-teal-100 text-teal-800">
                  {cluster.member_count} reports linked
                </span>
              </div>

              {/* Cluster links table */}
              <div className="divide-y divide-slate-100">
                {cluster.links.map((link) => (
                  <div key={link.id} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded border border-teal-200">
                          {link.issue_reference}
                        </span>
                        <span className="text-xs font-semibold text-slate-800">{link.issue_title}</span>
                        <span className="text-[11px] text-slate-400">({link.issue_category})</span>
                      </div>
                      <div className="text-xs text-slate-600 font-mono mt-0.5">
                        {link.similarity_explanation}
                      </div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-3">
                        <span>Distance: {Math.round(link.distance_km * 1000)}m</span>
                        <span>Similarity: {Math.round(link.similarity_score * 100)}%</span>
                        <span className="font-semibold text-slate-600">Review Status: {link.reviewed_status}</span>
                      </div>
                    </div>

                    {/* Review Actions */}
                    <div className="flex items-center gap-2 self-start md:self-auto flex-shrink-0">
                      {link.reviewed_status === 'pending_review' ? (
                        <>
                          <button
                            type="button"
                            disabled={reviewingId === link.id}
                            onClick={() => handleReviewAction(link.id, 'confirmed')}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-teal-600 text-white text-xs font-semibold hover:bg-teal-700 shadow-sm"
                          >
                            <CheckCircle className="w-3.5 h-3.5" />
                            Confirm Duplicate
                          </button>

                          <button
                            type="button"
                            disabled={reviewingId === link.id}
                            onClick={() => handleReviewAction(link.id, 'separated')}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 text-xs font-semibold hover:bg-slate-50"
                          >
                            <Split className="w-3.5 h-3.5" />
                            Separate
                          </button>

                          <button
                            type="button"
                            disabled={reviewingId === link.id}
                            onClick={() => handleReviewAction(link.id, 'dismissed')}
                            className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-rose-600 hover:bg-rose-50 text-xs font-semibold"
                          >
                            <XCircle className="w-3.5 h-3.5" />
                            Dismiss
                          </button>
                        </>
                      ) : (
                        <div className="flex items-center gap-1 text-xs font-bold text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg">
                          <span>Decision: {link.reviewed_status.toUpperCase()}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
