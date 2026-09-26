"use client";

import React from "react";
import { CheckCircle2, Clock, AlertTriangle, ShieldCheck, ArrowRight, ExternalLink } from "lucide-react";
import { RunItem } from "../lib/types";

interface RunHistoryProps {
  runs: RunItem[];
  onSelectRun: (runId: string) => void;
  selectedRunId?: string;
}

export const RunHistory: React.FC<RunHistoryProps> = ({ runs, onSelectRun, selectedRunId }) => {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-bold text-white">Historical Multi-Agent Runs & Audit Trail</h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Audit logging of past business requests, token costs, latencies, and human approval outcomes
          </p>
        </div>
        <span className="text-xs font-mono text-slate-500 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
          Total Runs: {runs.length}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-mono">
              <th className="pb-3 font-medium">RUN ID</th>
              <th className="pb-3 font-medium">BUSINESS DIRECTIVE</th>
              <th className="pb-3 font-medium">STATUS</th>
              <th className="pb-3 font-medium">TOKENS</th>
              <th className="pb-3 font-medium">COST</th>
              <th className="pb-3 font-medium text-right">ACTION</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {runs.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No multi-agent runs recorded yet. Execute a directive above!
                </td>
              </tr>
            ) : (
              runs.map((run) => (
                <tr
                  key={run.run_id}
                  className={`hover:bg-slate-800/40 transition-colors ${
                    selectedRunId === run.run_id ? "bg-blue-950/20" : ""
                  }`}
                >
                  <td className="py-3 font-mono font-medium text-blue-400">{run.run_id}</td>
                  <td className="py-3 text-slate-300 max-w-md truncate pr-4">{run.query}</td>
                  <td className="py-3">
                    {run.status === "COMPLETED" && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[11px] font-medium inline-flex items-center space-x-1">
                        <CheckCircle2 className="h-3 w-3" />
                        <span>Completed</span>
                      </span>
                    )}
                    {run.status === "WAITING_APPROVAL" && (
                      <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[11px] font-medium inline-flex items-center space-x-1">
                        <ShieldCheck className="h-3 w-3" />
                        <span>Needs Approval</span>
                      </span>
                    )}
                    {run.status === "RUNNING" && (
                      <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-[11px] font-medium inline-flex items-center space-x-1">
                        <Clock className="h-3 w-3 animate-spin" />
                        <span>Running</span>
                      </span>
                    )}
                    {run.status === "FAILED" && (
                      <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[11px] font-medium inline-flex items-center space-x-1">
                        <AlertTriangle className="h-3 w-3" />
                        <span>Failed</span>
                      </span>
                    )}
                  </td>
                  <td className="py-3 font-mono text-slate-400">{run.total_tokens.toLocaleString()}</td>
                  <td className="py-3 font-mono text-slate-400">${run.total_cost.toFixed(4)}</td>
                  <td className="py-3 text-right">
                    <button
                      onClick={() => onSelectRun(run.run_id)}
                      className="text-xs text-blue-400 hover:text-blue-300 font-medium inline-flex items-center space-x-1"
                    >
                      <span>Inspect</span>
                      <ArrowRight className="h-3 w-3" />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
