"use client";

import React, { useState } from "react";
import { Send, Sparkles, AlertCircle, ArrowRight, ShieldCheck, CheckCircle2 } from "lucide-react";

interface ChatInterfaceProps {
  onStartRun: (query: string) => Promise<void>;
  isLoading: boolean;
  stepHistory: Array<any>;
  onOpenApproval: () => void;
  hasPendingApproval: boolean;
}

const PRESET_QUERIES = [
  {
    title: "Quarterly Revenue Drop & Q4 Forecast (README Prompt)",
    query:
      "Analyze why our revenue dropped this quarter, compare product performance, investigate the likely causes, forecast next quarter, and prepare an evidence-backed report. Send it to the finance team after approval.",
  },
  {
    title: "DataSync Appliance Anomaly Investigation",
    query:
      "Investigate products showing steeper than 30% revenue drops in Q3, retrieve operational memos, verify supplier impacts, and report root causes.",
  },
  {
    title: "EMEA Telecom Renewal Slip Analysis",
    query:
      "Analyze EMEA regional sales softness in Q3, cross-examine compliance audit deferrals, and project deal recovery for Q4.",
  },
];

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  onStartRun,
  isLoading,
  stepHistory,
  onOpenApproval,
  hasPendingApproval,
}) => {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onStartRun(query);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center space-x-2 mb-4">
        <Sparkles className="h-5 w-5 text-blue-400" />
        <h3 className="text-base font-semibold text-white">Business Intelligence Directive</h3>
      </div>

      {/* Preset Pills */}
      <div className="mb-4">
        <span className="text-xs font-medium text-slate-400 block mb-2">Preset Enterprise Directives:</span>
        <div className="flex flex-wrap gap-2">
          {PRESET_QUERIES.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => setQuery(preset.query)}
              className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700 transition-colors text-left"
            >
              {preset.title}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Instruct the multi-agent system (e.g. 'Analyze why our revenue dropped this quarter...')"
            rows={3}
            className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Enforced policies: Gemini 2.5 Flash · Read-only Data MCP · Critic Arithmetic QA · Human-in-the-loop Gate
          </span>

          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className={`px-5 py-2.5 rounded-xl text-sm font-semibold flex items-center space-x-2 transition-all shadow-lg ${
              isLoading || !query.trim()
                ? "bg-slate-800 text-slate-500 cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/30 active:scale-95"
            }`}
          >
            {isLoading ? (
              <>
                <div className="h-4 w-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                <span>Coordinating Agents...</span>
              </>
            ) : (
              <>
                <span>Execute Multi-Agent Run</span>
                <Send className="h-4 w-4" />
              </>
            )}
          </button>
        </div>
      </form>

      {/* Step History Trace */}
      {stepHistory.length > 0 && (
        <div className="mt-6 pt-6 border-t border-slate-800">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Live Agent Execution Steps ({stepHistory.length})
            </h4>
            {hasPendingApproval && (
              <button
                onClick={onOpenApproval}
                className="text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold px-3 py-1 rounded-lg flex items-center space-x-1.5 shadow-md shadow-amber-500/20"
              >
                <ShieldCheck className="h-3.5 w-3.5" />
                <span>Review Pending Action</span>
              </button>
            )}
          </div>

          <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
            {stepHistory.map((step, idx) => (
              <div
                key={idx}
                className="flex items-start space-x-3 p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 text-xs"
              >
                <div className="mt-0.5">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200 capitalize">
                      {step.agent || step.step} Agent
                    </span>
                    <span className="text-slate-500 font-mono text-[11px]">
                      {step.latency_ms ? `${step.latency_ms}ms` : ""}
                    </span>
                  </div>
                  <p className="text-slate-400 mt-0.5">{step.summary}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
