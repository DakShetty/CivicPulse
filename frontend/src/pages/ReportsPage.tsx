import React, { useState, useEffect } from 'react';
import { ReportRecord } from '../types';
import { api } from '../api/client';
import { FileText, Download, FileSpreadsheet, PlusCircle, CheckCircle, Clock } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const fetchReports = async () => {
    try {
      const data = await api.getReports();
      setReports(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerate = async (type: 'summary_csv' | 'summary_pdf') => {
    setGenerating(true);
    setMessage(null);
    try {
      const res = await api.generateReport(type);
      setMessage(`Generated report: ${res.report.title}`);
      await fetchReports();
    } catch (err: any) {
      alert(err.message || 'Report generation failed');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <FileText className="w-6 h-6 text-teal-600" />
            Civic Operations Reports & Compliance Exports
          </h1>
          <p className="text-xs text-slate-600 mt-1">
            Generate and download encrypted CSV datasets and PDF executive briefings stored in private S3.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={generating}
            onClick={() => handleGenerate('summary_csv')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800 disabled:opacity-50 transition shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            <span>Generate CSV</span>
          </button>

          <button
            type="button"
            disabled={generating}
            onClick={() => handleGenerate('summary_pdf')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-teal-600 text-white text-xs font-semibold hover:bg-teal-700 disabled:opacity-50 transition shadow-sm"
          >
            <FileText className="w-4 h-4 text-white" />
            <span>Generate PDF Brief</span>
          </button>
        </div>
      </div>

      {message && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {/* Reports Archive */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center text-xs">
          <span className="font-bold text-slate-700">Generated Reports Archive</span>
          <span className="text-slate-400 font-mono">Short-Lived Signed Download URLs</span>
        </div>

        <div className="divide-y divide-slate-100">
          {loading ? (
            <div className="p-8 text-center text-xs text-slate-500">Loading reports...</div>
          ) : reports.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-400">
              No reports generated yet. Click "Generate CSV" or "Generate PDF Brief" above.
            </div>
          ) : (
            reports.map((r) => (
              <div key={r.id} className="p-4 flex items-center justify-between hover:bg-slate-50">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600">
                    {r.report_type.includes('csv') ? (
                      <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
                    ) : (
                      <FileText className="w-5 h-5 text-teal-600" />
                    )}
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900">{r.title}</h4>
                    <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                      Type: {r.report_type} &bull; Size: {Math.round(r.file_size_bytes / 1024)} KB &bull;{' '}
                      {new Date(r.created_at).toLocaleString()}
                    </div>
                  </div>
                </div>

                {r.download_url ? (
                  <a
                    href={r.download_url}
                    download
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100 transition"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Download</span>
                  </a>
                ) : (
                  <span className="text-xs text-slate-400">Processing...</span>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
