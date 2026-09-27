"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import { MetricsOverview } from "../components/MetricsOverview";
import { WorkflowGraph } from "../components/WorkflowGraph";
import { ChatInterface } from "../components/ChatInterface";
import { ApprovalGateModal } from "../components/ApprovalGateModal";
import { ReportViewer } from "../components/ReportViewer";
import { RunHistory } from "../components/RunHistory";
import { ToolsCatalog } from "../components/ToolsCatalog";
import {
  createRun,
  getRuns,
  getRunDetails,
  approveRun,
  rejectRun,
  getMetrics,
  getTools,
} from "../lib/api";
import { RunDetail, RunItem, SystemMetrics, ToolDefinition } from "../lib/types";

export default function Home() {
  const [activeTab, setActiveTab] = useState("orchestrator");
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [currentRun, setCurrentRun] = useState<RunDetail | null>(null);
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [tools, setTools] = useState<ToolDefinition[]>([]);
  const [permissionMatrix, setPermissionMatrix] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);

  // Initial data loading
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [runsData, metricsData, toolsData] = await Promise.all([
        getRuns().catch(() => ({ runs: [] })),
        getMetrics().catch(() => null),
        getTools().catch(() => ({ tools: [], permission_matrix: {} })),
      ]);
      setRuns(runsData.runs);
      if (metricsData) setMetrics(metricsData);
      setTools(toolsData.tools);
      setPermissionMatrix(toolsData.permission_matrix);

      // If there are past runs, load the latest one
      if (runsData.runs.length > 0 && !currentRun) {
        const latest = await getRunDetails(runsData.runs[0].run_id).catch(() => null);
        if (latest) setCurrentRun(latest);
      }
    } catch (err) {
      console.error("Error loading initial data", err);
    }
  };

  // Start new multi-agent run with live SSE stream
  const handleStartRun = async (query: string) => {
    setIsLoading(true);
    try {
      const { run_id } = await createRun(query);

      // Initialize run state
      const initialDetail: RunDetail = {
        run_id,
        query,
        status: "RUNNING",
        current_node: "planner",
        step_history: [],
        total_tokens: 0,
        total_cost: 0,
      };
      setCurrentRun(initialDetail);

      // Connect to SSE stream
      const eventSource = new EventSource(`http://localhost:8000/api/v1/runs/${run_id}/stream`);

      eventSource.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.event === "node_completed") {
            const updated = await getRunDetails(run_id);
            setCurrentRun(updated);

            if (updated.status === "WAITING_APPROVAL") {
              setIsApprovalOpen(true);
            }
          } else if (data.event === "run_finished" || data.event === "run_failed") {
            const finalState = await getRunDetails(run_id);
            setCurrentRun(finalState);
            setIsLoading(false);
            eventSource.close();
            loadInitialData();
          }
        } catch (e) {
          console.error("SSE parse error", e);
        }
      };

      eventSource.onerror = async () => {
        eventSource.close();
        setIsLoading(false);
        const finalState = await getRunDetails(run_id).catch(() => null);
        if (finalState) setCurrentRun(finalState);
        loadInitialData();
      };
    } catch (err: any) {
      alert(`Error starting run: ${err.message}`);
      setIsLoading(false);
    }
  };

  const handleApprove = async (comment: string) => {
    if (!currentRun) return;
    try {
      await approveRun(currentRun.run_id, comment);
      const updated = await getRunDetails(currentRun.run_id);
      setCurrentRun(updated);
      loadInitialData();
    } catch (e: any) {
      alert(`Approval error: ${e.message}`);
    }
  };

  const handleReject = async (reason: string) => {
    if (!currentRun) return;
    try {
      await rejectRun(currentRun.run_id, reason);
      const updated = await getRunDetails(currentRun.run_id);
      setCurrentRun(updated);
      loadInitialData();
    } catch (e: any) {
      alert(`Rejection error: ${e.message}`);
    }
  };

  const handleSelectRun = async (runId: string) => {
    const detail = await getRunDetails(runId).catch(() => null);
    if (detail) {
      setCurrentRun(detail);
      setActiveTab("orchestrator");
    }
  };

  const pendingApprovalsCount = runs.filter((r) => r.status === "WAITING_APPROVAL").length;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        pendingApprovalsCount={pendingApprovalsCount}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* KPI Metrics Banner */}
        <MetricsOverview metrics={metrics} />

        {/* Tab 1: Agent Orchestrator & Live Workspace */}
        {activeTab === "orchestrator" && (
          <div className="space-y-6">
            <WorkflowGraph
              currentNode={currentRun?.current_node || "IDLE"}
              status={currentRun?.status || "IDLE"}
              stepHistory={currentRun?.step_history || []}
              approvalStatus={currentRun?.approval_status}
            />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChatInterface
                onStartRun={handleStartRun}
                isLoading={isLoading}
                stepHistory={currentRun?.step_history || []}
                onOpenApproval={() => setIsApprovalOpen(true)}
                hasPendingApproval={currentRun?.status === "WAITING_APPROVAL"}
              />

              <ReportViewer
                reportContent={currentRun?.report_results?.report_content}
                reportId={currentRun?.report_results?.report_id}
                approvalStatus={currentRun?.approval_status}
              />
            </div>
          </div>
        )}

        {/* Tab 2: Approvals View */}
        {activeTab === "approvals" && (
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <h3 className="text-lg font-bold text-white mb-2">Human Approval Governance Queue</h3>
              <p className="text-xs text-slate-400 mb-6">
                All consequential multi-agent actions (such as sending executive emails or updating CRM systems) are held in state until authorized by a human reviewer.
              </p>

              {currentRun?.status === "WAITING_APPROVAL" ? (
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-amber-300">Action Pending Review: {currentRun.approval_record?.action_type}</h4>
                    <p className="text-xs text-slate-300 mt-1">{currentRun.approval_record?.summary}</p>
                  </div>
                  <button
                    onClick={() => setIsApprovalOpen(true)}
                    className="px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs"
                  >
                    Open Review Modal
                  </button>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 text-sm">
                  No actions currently pending approval. Run a business directive requesting report delivery!
                </div>
              )}
            </div>
          </div>
        )}

        {/* Tab 3: Run History */}
        {activeTab === "history" && (
          <RunHistory
            runs={runs}
            onSelectRun={handleSelectRun}
            selectedRunId={currentRun?.run_id}
          />
        )}

        {/* Tab 4: MCP Tools & RBAC Matrix */}
        {activeTab === "tools" && (
          <ToolsCatalog tools={tools} permissionMatrix={permissionMatrix} />
        )}
      </main>

      {/* Human Approval Gate Modal */}
      <ApprovalGateModal
        isOpen={isApprovalOpen}
        onClose={() => setIsApprovalOpen(false)}
        approvalRecord={currentRun?.approval_record}
        onApprove={handleApprove}
        onReject={handleReject}
        runId={currentRun?.run_id || ""}
      />

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <p>Enterprise Multi-Agent AI System · Powered by Google Gemini API, LangGraph, and Model Context Protocol (MCP)</p>
      </footer>
    </div>
  );
}
