import React from 'react';
import { ShieldCheck, Play, RefreshCw } from 'lucide-react';

export default function Header({ onTriggerAudit, isAuditing }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-emerald-500/10 border border-emerald-500/30 p-2 rounded-lg">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-100 flex items-center space-x-2">
              <span>CodeReviewer Pro</span>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400">
                Agent v1.0
              </span>
            </h1>
            <p className="text-xs text-slate-400">Autonomous Multi-Repo PR Auditor</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onTriggerAudit}
            disabled={isAuditing}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-medium bg-emerald-500 hover:bg-emerald-400 text-slate-950 transition duration-150 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20"
          >
            {isAuditing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Auditing Diff...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Run Test PR Audit</span>
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}