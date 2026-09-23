import { RunDetail, RunItem, SystemMetrics, ToolDefinition } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export async function createRun(query: string): Promise<{ run_id: string; status: string }> {
  const res = await fetch(`${BASE_URL}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to trigger run");
  }
  return res.json();
}

export async function getRuns(): Promise<{ runs: RunItem[] }> {
  const res = await fetch(`${BASE_URL}/runs`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch runs");
  return res.json();
}

export async function getRunDetails(runId: string): Promise<RunDetail> {
  const res = await fetch(`${BASE_URL}/runs/${runId}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch run ${runId}`);
  return res.json();
}

export async function approveRun(runId: string, comment?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/runs/${runId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision: "APPROVED", comment: comment || "Approved by executive reviewer" }),
  });
  if (!res.ok) throw new Error("Approval failed");
  return res.json();
}

export async function rejectRun(runId: string, reason?: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/runs/${runId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ decision: "REJECTED", comment: reason || "Rejected by reviewer" }),
  });
  if (!res.ok) throw new Error("Rejection failed");
  return res.json();
}

export async function getMetrics(): Promise<SystemMetrics> {
  const res = await fetch(`${BASE_URL}/metrics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch metrics");
  return res.json();
}

export async function getTools(): Promise<{ tools: ToolDefinition[]; permission_matrix: Record<string, string[]> }> {
  const res = await fetch(`${BASE_URL}/tools`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch tools catalog");
  return res.json();
}
