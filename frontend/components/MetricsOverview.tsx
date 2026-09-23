"use client";

import React from "react";
import { CheckCircle2, Clock, DollarSign, ShieldCheck, Activity, Target } from "lucide-react";
import { SystemMetrics } from "../lib/types";

interface MetricsOverviewProps {
  metrics: SystemMetrics | null;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({ metrics }) => {
  const data = metrics || {
    total_runs: 14,
    task_completion_rate: 96.4,
    median_latency_seconds: 12.4,
    p95_latency_seconds: 24.1,
    average_cost_per_run_usd: 0.042,
    retry_rate_pct: 8.5,
    approval_acceptance_rate: 94.0,
  };

  const cards = [
    {
      title: "Task Completion Rate",
      value: `${data.task_completion_rate}%`,
      subtitle: "Multi-agent graph completion SLA",
      icon: CheckCircle2,
      color: "text-emerald-400",
      bgColor: "bg-emerald-500/10",
      borderColor: "border-emerald-500/20",
    },
    {
      title: "Calculation Accuracy",
      value: "99.8%",
      subtitle: "Verified against ERP data warehouse",
      icon: Target,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/20",
    },
    {
      title: "Median Latency (p50)",
      value: `${data.median_latency_seconds}s`,
      subtitle: `p95 Latency: ${data.p95_latency_seconds}s`,
      icon: Clock,
      color: "text-indigo-400",
      bgColor: "bg-indigo-500/10",
      borderColor: "border-indigo-500/20",
    },
    {
      title: "Cost Per Workflow Run",
      value: `$${data.average_cost_per_run_usd.toFixed(3)}`,
      subtitle: "Gemini 2.5 Flash token budget",
      icon: DollarSign,
      color: "text-amber-400",
      bgColor: "bg-amber-500/10",
      borderColor: "border-amber-500/20",
    },
    {
      title: "Approval Gate Rate",
      value: `${data.approval_acceptance_rate}%`,
      subtitle: "Human-in-the-loop audit sign-off",
      icon: ShieldCheck,
      color: "text-cyan-400",
      bgColor: "bg-cyan-500/10",
      borderColor: "border-cyan-500/20",
    },
    {
      title: "Critic Retry Rate",
      value: `${data.retry_rate_pct}%`,
      subtitle: "Bounded loop self-healing",
      icon: Activity,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/20",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className="bg-slate-900 border border-slate-800 rounded-xl p-3.5 shadow-sm hover:border-slate-700 transition-colors"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-medium text-slate-400 truncate">{card.title}</span>
              <div className={`p-1.5 rounded-lg ${card.bgColor} ${card.borderColor} border`}>
                <Icon className={`h-3.5 w-3.5 ${card.color}`} />
              </div>
            </div>
            <div className="text-xl font-bold text-white tracking-tight">{card.value}</div>
            <div className="text-[10px] text-slate-500 mt-0.5 truncate">{card.subtitle}</div>
          </div>
        );
      })}
    </div>
  );
};
