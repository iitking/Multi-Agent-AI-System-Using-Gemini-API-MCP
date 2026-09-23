"use client";

import React from "react";
import { ShieldCheck, Cpu, Database, Activity, GitBranch } from "lucide-react";

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  pendingApprovalsCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, pendingApprovalsCount }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-sky-400 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <Cpu className="h-6 w-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">ApexCloud</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 font-medium">
                Gemini + MCP
              </span>
            </div>
            <p className="text-xs text-slate-400">Enterprise Multi-Agent AI System</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActiveTab("orchestrator")}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === "orchestrator"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                : "text-slate-300 hover:text-white hover:bg-slate-800"
            }`}
          >
            <GitBranch className="h-4 w-4" />
            <span>Agent Graph</span>
          </button>

          <button
            onClick={() => setActiveTab("approvals")}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 relative ${
              activeTab === "approvals"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                : "text-slate-300 hover:text-white hover:bg-slate-800"
            }`}
          >
            <ShieldCheck className="h-4 w-4" />
            <span>Approvals</span>
            {pendingApprovalsCount > 0 && (
              <span className="ml-1 px-1.5 py-0.2 bg-amber-500 text-slate-950 text-xs font-bold rounded-full animate-pulse">
                {pendingApprovalsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("history")}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === "history"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                : "text-slate-300 hover:text-white hover:bg-slate-800"
            }`}
          >
            <Activity className="h-4 w-4" />
            <span>Run History</span>
          </button>

          <button
            onClick={() => setActiveTab("tools")}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center space-x-1.5 ${
              activeTab === "tools"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/20"
                : "text-slate-300 hover:text-white hover:bg-slate-800"
            }`}
          >
            <Database className="h-4 w-4" />
            <span>MCP Tools</span>
          </button>
        </nav>

        {/* User Identity */}
        <div className="hidden md:flex items-center space-x-3 text-xs border-l border-slate-800 pl-4">
          <div className="flex flex-col text-right">
            <span className="text-slate-200 font-semibold">analyst_jane</span>
            <span className="text-slate-400">Security: RBAC Analyst</span>
          </div>
          <div className="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-sky-400">
            J
          </div>
        </div>
      </div>
    </header>
  );
};
