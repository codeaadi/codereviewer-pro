import React from 'react';
import { X, AlertCircle, AlertTriangle, Info, Check, Copy } from 'lucide-react';

export default function ReviewModal({ review, onClose }) {
  if (!review) return null;

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'critical':
        return {
          icon: AlertCircle,
          className: 'bg-red-500/10 border-red-500/30 text-red-400',
        };
      case 'warning':
        return {
          icon: AlertTriangle,
          className: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
        };
      default:
        return {
          icon: Info,
          className: 'bg-blue-500/10 border-blue-500/30 text-blue-400',
        };
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-100 flex items-center space-x-2">
              <span>Security Audit Findings</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-mono font-medium ${
                review.security_risk_score > 70
                  ? 'bg-red-500/10 border border-red-500/30 text-red-400'
                  : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
              }`}>
                Risk Score: {review.security_risk_score}/100
              </span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">Execution latency: {review.execution_time_ms}ms · Tokens: {review.token_usage}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-5">
          {/* Summary Box */}
          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
            <h3 className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-1.5">Executive Summary</h3>
            <p className="text-sm text-slate-300 leading-relaxed">{review.summary}</p>
          </div>

          {/* Line by Line Comments */}
          <div>
            <h3 className="text-xs uppercase tracking-wider font-semibold text-slate-400 mb-3">
              Identified Vulnerabilities ({review.comments?.length || 0})
            </h3>
            <div className="space-y-3">
              {review.comments?.map((comment) => {
                const badge = getSeverityBadge(comment.severity);
                const Icon = badge.icon;
                return (
                  <div
                    key={comment.id}
                    className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 space-y-3"
                  >
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center space-x-2 font-mono">
                        <span className="text-slate-300 font-semibold">{comment.file_path}</span>
                        <span className="text-slate-500">line {comment.line_number}</span>
                      </div>
                      <div className={`flex items-center space-x-1.5 px-2 py-0.5 rounded-full border text-[11px] uppercase font-mono ${badge.className}`}>
                        <Icon className="w-3 h-3" />
                        <span>{comment.severity}</span>
                      </div>
                    </div>

                    <p className="text-sm text-slate-300">{comment.message}</p>

                    {comment.suggested_patch && (
                      <div className="rounded-lg bg-slate-900 border border-slate-800 p-3 overflow-x-auto font-mono text-xs text-emerald-300">
                        <div className="text-[10px] text-slate-400 uppercase tracking-wider mb-1 font-sans">Suggested Remediation:</div>
                        <pre className="whitespace-pre-wrap">{comment.suggested_patch}</pre>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}