export interface StepHistoryItem {
  step: string;
  agent: string;
  status: string;
  latency_ms?: number;
  tokens?: number;
  tool_calls?: number;
  score?: number;
  summary?: string;
}

export interface ApprovalRecord {
  action_type: string;
  recipient?: string;
  subject?: string;
  summary: string;
  approval_token: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  approved_by?: string;
  rejection_reason?: string;
}

export interface RunItem {
  run_id: string;
  query: string;
  status: "PENDING" | "RUNNING" | "WAITING_APPROVAL" | "COMPLETED" | "FAILED" | "ESCALATED";
  current_node?: string;
  approval_status?: string;
  has_approval_pending?: boolean;
  total_tokens: number;
  total_cost: number;
  steps_count: number;
}

export interface RunDetail {
  run_id: string;
  query: string;
  status: "PENDING" | "RUNNING" | "WAITING_APPROVAL" | "COMPLETED" | "FAILED" | "ESCALATED";
  current_node: string;
  plan?: {
    summary: string;
    tasks: Array<{
      task_id: string;
      agent: string;
      tools: string[];
      dependencies: string[];
    }>;
    requires_human_approval?: boolean;
  };
  analytics_results?: {
    metrics?: Record<string, any>;
    anomalies?: Array<any>;
    summary_data?: any;
  };
  research_results?: {
    evidence?: Array<{
      source: string;
      title: string;
      findings: string;
      confidence: number;
    }>;
    summary?: string;
  };
  forecast_results?: {
    forecast?: {
      forecast_quarter?: string;
      scenarios?: Record<string, any>;
      root_cause_attribution?: Record<string, string>;
    };
  };
  critic_results?: {
    quality_passed?: boolean;
    score?: number;
    verification_checks?: Record<string, string>;
    issues?: string[];
  };
  report_results?: {
    report_content?: string;
    report_id?: string;
  };
  approval_record?: ApprovalRecord;
  approval_status?: string;
  action_execution_result?: any;
  step_history: StepHistoryItem[];
  total_tokens: number;
  total_cost: number;
}

export interface SystemMetrics {
  total_runs: number;
  task_completion_rate: number;
  median_latency_seconds: number;
  p95_latency_seconds: number;
  average_cost_per_run_usd: number;
  retry_rate_pct: number;
  approval_acceptance_rate: number;
}

export interface ToolDefinition {
  name: string;
  description: string;
  server_name: string;
  parameters: any;
}
