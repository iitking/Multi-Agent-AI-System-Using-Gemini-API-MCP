"use client";

import React from "react";
import { Database, Search, FileText, Send, Shield, Lock, CheckCircle2, XCircle } from "lucide-react";
import { ToolDefinition } from "../lib/types";

interface ToolsCatalogProps {
  tools: ToolDefinition[];
  permissionMatrix: Record<string, string[]>;
}

export const ToolsCatalog: React.FC<ToolsCatalogProps> = ({ tools, permissionMatrix }) => {
  const servers = [
    {
      name: "Data_MCP_Server",
      desc: "Queries financial data warehouse, calculates QoQ KPI variances, detects anomalies.",
      icon: Database,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10 border-cyan-500/20",
    },
    {
      name: "Research_MCP_Server",
      desc: "Retrieves internal memos, supplier notices, market reports, and compliance audit citations.",
      icon: Search,
      color: "text-indigo-400",
      bg: "bg-indigo-500/10 border-indigo-500/20",
    },
    {
      name: "Document_MCP_Server",
      desc: "Renders structured executive intelligence reports and persists markdown artifacts.",
      icon: FileText,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10 border-emerald-500/20",
    },
    {
      name: "Automation_MCP_Server",
      desc: "Dispatches approved emails, Slack alerts, and CRM tasks via n8n integration with approval gate tokens.",
      icon: Send,
      color: "text-amber-400",
      bg: "bg-amber-500/10 border-amber-500/20",
    },
  ];

  return (
    <div className="space-y-6">
      {/* MCP Servers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {servers.map((srv, idx) => {
          const Icon = srv.icon;
          return (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg space-y-3">
              <div className={`h-10 w-10 rounded-xl ${srv.bg} border flex items-center justify-center`}>
                <Icon className={`h-5 w-5 ${srv.color}`} />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{srv.name}</h4>
                <p className="text-xs text-slate-400 mt-1 leading-relaxed">{srv.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* RBAC Permission Matrix */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-blue-400" />
          <h3 className="text-base font-bold text-white">Agent-to-Tool Authorization Allowlist (RBAC)</h3>
        </div>
        <p className="text-xs text-slate-400">
          Strict policy boundaries enforced in code: Agents are strictly prohibited from calling unpermitted tools or bypassing approval gates.
        </p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-mono">
                <th className="pb-3 font-medium">AGENT ROLE</th>
                <th className="pb-3 font-medium">PERMITTED MCP TOOLS</th>
                <th className="pb-3 font-medium">CONSEQUENTIAL ACTION GATE</th>
                <th className="pb-3 font-medium">POLICY ENFORCEMENT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {Object.entries(permissionMatrix).map(([agent, toolList], idx) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-3 font-semibold text-slate-200 capitalize">{agent} Agent</td>
                  <td className="py-3">
                    <div className="flex flex-wrap gap-1.5">
                      {toolList.length === 0 ? (
                        <span className="text-slate-500 italic text-[11px]">None (Reasoning & Orchestration only)</span>
                      ) : (
                        toolList.map((t, tidx) => (
                          <span
                            key={tidx}
                            className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300 font-mono text-[10px]"
                          >
                            {t}
                          </span>
                        ))
                      )}
                    </div>
                  </td>
                  <td className="py-3">
                    {agent === "action_executor" ? (
                      <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[10px] font-bold">
                        MANDATORY HUMAN TOKEN
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-[10px]">
                        Read-Only / Safe
                      </span>
                    )}
                  </td>
                  <td className="py-3">
                    <span className="inline-flex items-center space-x-1 text-emerald-400 text-[11px] font-medium">
                      <CheckCircle2 className="h-3 w-3" />
                      <span>Enforced in PolicyEngine</span>
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
