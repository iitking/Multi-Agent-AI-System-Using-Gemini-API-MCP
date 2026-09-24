"use client";

import React from "react";
import { CheckCircle2, Clock, AlertTriangle, ArrowRight, ShieldCheck, Mail, Database, Search, Cpu, FileText, Activity } from "lucide-react";

interface WorkflowGraphProps {
  currentNode: string;
  status: string;
  stepHistory: Array<{
    step: string;
    agent: string;
    status: string;
    latency_ms?: number;
    tokens?: number;
    score?: number;
    summary?: string;
  }>;
  approvalStatus?: string;
}

export const WorkflowGraph: React.FC<WorkflowGraphProps> = ({
  currentNode,
  status,
  stepHistory,
  approvalStatus,
}) => {
  const isCompleted = (nodeName: string) =>
    stepHistory.some((s) => s.step.toLowerCase() === nodeName.toLowerCase());

  const isActive = (nodeName: string) =>
    currentNode.toLowerCase() === nodeName.toLowerCase() && status === "RUNNING";

  const isWaitingApproval = status === "WAITING_APPROVAL";

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-base font-semibold text-white flex items-center space-x-2">
            <span>LangGraph Multi-Agent Orchestration Flow</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              Stateful Graph
            </span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time supervisor routing, parallel specialist execution, critic loop, and human approval gate
          </p>
        </div>

        <div className="flex items-center space-x-2">
          {status === "RUNNING" && (
            <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-medium">
              <span className="h-2 w-2 rounded-full bg-blue-400 animate-ping" />
              <span>Orchestrating</span>
            </span>
          )}
          {status === "WAITING_APPROVAL" && (
            <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-medium">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Awaiting Human Approval</span>
            </span>
          )}
          {status === "COMPLETED" && (
            <span className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-medium">
              <CheckCircle2 className="h-3.5 w-3.5" />
              <span>Workflow Finished</span>
            </span>
          )}
        </div>
      </div>

      {/* Visual Agent Pipeline */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-3 relative">
        {/* Node 1: Planner */}
        <div
          className={`p-3.5 rounded-xl border transition-all ${
            isActive("planner")
              ? "bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-500/10 ring-2 ring-blue-500/30"
              : isCompleted("planner")
              ? "bg-slate-800/80 border-slate-700 text-slate-200"
              : "bg-slate-900/60 border-slate-800 text-slate-500"
          }`}
        >
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-mono font-semibold text-blue-400">01. SUPERVISOR</span>
            {isCompleted("planner") && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
          </div>
          <div className="flex items-center space-x-2">
            <Cpu className="h-4 w-4 text-blue-400" />
            <h4 className="text-sm font-bold text-white">Planner Agent</h4>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Task decomposition & graph dependencies</p>
        </div>

        {/* Node 2: Analytics & Research (Parallel Specialists) */}
        <div className="md:col-span-2 space-y-2">
          {/* Analytics */}
          <div
            className={`p-3 rounded-xl border transition-all ${
              isActive("analytics")
                ? "bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-500/10 ring-2 ring-blue-500/30"
                : isCompleted("analytics")
                ? "bg-slate-800/80 border-slate-700 text-slate-200"
                : "bg-slate-900/60 border-slate-800 text-slate-500"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-mono font-semibold text-cyan-400">02A. SPECIALIST (PARALLEL)</span>
              {isCompleted("analytics") && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
            </div>
            <div className="flex items-center space-x-2">
              <Database className="h-4 w-4 text-cyan-400" />
              <h4 className="text-xs font-bold text-white">Analytics Agent (Data MCP)</h4>
            </div>
            <p className="text-[10px] text-slate-400 mt-0.5">KPIs, variance math & anomaly detection</p>
          </div>

          {/* Research */}
          <div
            className={`p-3 rounded-xl border transition-all ${
              isActive("researcher")
                ? "bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-500/10 ring-2 ring-blue-500/30"
                : isCompleted("researcher")
                ? "bg-slate-800/80 border-slate-700 text-slate-200"
                : "bg-slate-900/60 border-slate-800 text-slate-500"
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] font-mono font-semibold text-indigo-400">02B. SPECIALIST (PARALLEL)</span>
              {isCompleted("researcher") && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
            </div>
            <div className="flex items-center space-x-2">
              <Search className="h-4 w-4 text-indigo-400" />
              <h4 className="text-xs font-bold text-white">Research Agent (Research MCP)</h4>
            </div>
            <p className="text-[10px] text-slate-400 mt-0.5">Internal memos, vendor delays & citations</p>
          </div>
        </div>

        {/* Node 3: Forecaster */}
        <div
          className={`p-3.5 rounded-xl border transition-all ${
            isActive("forecaster")
              ? "bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-500/10 ring-2 ring-blue-500/30"
              : isCompleted("forecaster")
              ? "bg-slate-800/80 border-slate-700 text-slate-200"
              : "bg-slate-900/60 border-slate-800 text-slate-500"
          }`}
        >
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-mono font-semibold text-purple-400">03. SYNTHESIS</span>
            {isCompleted("forecaster") && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
          </div>
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-purple-400" />
            <h4 className="text-sm font-bold text-white">Forecaster</h4>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Base / Bull / Bear scenario modeling</p>
        </div>

        {/* Node 4: Critic */}
        <div
          className={`p-3.5 rounded-xl border transition-all ${
            isActive("critic")
              ? "bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-500/10 ring-2 ring-blue-500/30"
              : isCompleted("critic")
              ? "bg-slate-800/80 border-slate-700 text-slate-200"
              : "bg-slate-900/60 border-slate-800 text-slate-500"
          }`}
        >
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-mono font-semibold text-emerald-400">04. QUALITY GATE</span>
            {isCompleted("critic") && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
          </div>
          <div className="flex items-center space-x-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <h4 className="text-sm font-bold text-white">Critic Agent</h4>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Arithmetic checks & bounded retry loop</p>
        </div>

        {/* Node 5: Reporter & Human Approval Gate */}
        <div
          className={`p-3.5 rounded-xl border transition-all ${
            isWaitingApproval
              ? "bg-amber-950/40 border-amber-500 shadow-lg shadow-amber-500/10 ring-2 ring-amber-500/40 animate-pulse"
              : isCompleted("reporter")
              ? "bg-slate-800/80 border-slate-700 text-slate-200"
              : "bg-slate-900/60 border-slate-800 text-slate-500"
          }`}
        >
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs font-mono font-semibold text-amber-400">05. APPROVAL GATE</span>
            {approvalStatus === "APPROVED" && <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />}
          </div>
          <div className="flex items-center space-x-2">
            <FileText className="h-4 w-4 text-amber-400" />
            <h4 className="text-sm font-bold text-white">Reporter & Action</h4>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            {isWaitingApproval ? "Consequential action requires review" : "Final executive report delivery"}
          </p>
        </div>
      </div>
    </div>
  );
};
