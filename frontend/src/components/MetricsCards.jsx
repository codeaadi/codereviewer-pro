import React from "react";
import { GitPullRequest, AlertTriangle, ShieldAlert, Cpu } from "lucide-react";

export default function MetricsCards({ reviews }) {
  const totalReviews = reviews.length;
  const criticalCount = reviews.reduce((acc, r) => {
    return (
      acc + (r.comments?.filter((c) => c.severity === "critical").length || 0)
    );
  }, 0);

  const avgRisk =
    totalReviews > 0
      ? Math.round(
          reviews.reduce((acc, r) => acc + (r.security_risk_score || 0), 0) /
            totalReviews,
        )
      : 0;

  const avgLatency =
    totalReviews > 0
      ? Math.round(
          reviews.reduce((acc, r) => acc + (r.execution_time_ms || 0), 0) /
            totalReviews,
        )
      : 0;
  const cards = [
    {
      title: "Audited Reviews",
      value: totalReviews,
      icon: GitPullRequest,
      accent: "text-blue-400",
      bg: "bg-blue-500/10 border-blue-500/20",
    },
    {
      title: "Critical CVEs Caught",
      value: criticalCount,
      icon: AlertTriangle,
      accent: "text-red-400",
      bg: "bg-red-500/10 border-red-500/20",
    },
    {
      title: "Avg Security Risk",
      value: `${avgRisk}/100`,
      icon: ShieldAlert,
      accent: avgRisk > 70 ? "text-rose-400" : "text-emerald-400",
      bg:
        avgRisk > 70
          ? "bg-rose-500/10 border-rose-500/20"
          : "bg-emerald-500/10 border-emerald-500/20",
    },
    {
      title: "Avg Inference Time",
      value: `${avgLatency} ms`,
      icon: Cpu,
      accent: "text-amber-400",
      bg: "bg-amber-500/10 border-amber-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, i) => {
        const Icon = card.icon;
        return (
          <div
            key={i}
            className="p-4 rounded-xl border border-slate-800 bg-slate-900/40 backdrop-blur-sm flex items-center justify-between"
          >
            <div>
              <p className="text-xs text-slate-400 font-medium">{card.title}</p>
              <p className="text-2xl font-bold text-slate-100 mt-1 font-mono">
                {card.value}
              </p>
            </div>
            <div className={`p-2.5 rounded-lg border ${card.bg}`}>
              <Icon className={`w-5 h-5 ${card.accent}`} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
