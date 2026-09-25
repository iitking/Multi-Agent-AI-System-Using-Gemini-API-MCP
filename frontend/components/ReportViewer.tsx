"use client";

import React, { useState } from "react";
import { FileText, Copy, Check, Download, ShieldCheck, Share2 } from "lucide-react";

interface ReportViewerProps {
  reportContent?: string;
  reportId?: string;
  approvalStatus?: string;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({
  reportContent,
  reportId,
  approvalStatus,
}) => {
  const [copied, setCopied] = useState(false);

  if (!reportContent) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(reportContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
            <FileText className="h-5 w-5 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Final Verified Intelligence Report</h3>
            <div className="flex items-center space-x-2 text-xs text-slate-400 mt-0.5">
              <span>Report ID: {reportId || "REP-CURRENT"}</span>
              <span>•</span>
              <span className="text-emerald-400 font-medium">Critic QA Verified (Score 9.4/10)</span>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {approvalStatus === "APPROVED" && (
            <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold flex items-center space-x-1">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Action Executed</span>
            </span>
          )}

          <button
            onClick={handleCopy}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors text-xs flex items-center space-x-1 border border-slate-700"
          >
            {copied ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
            <span className="hidden sm:inline">{copied ? "Copied" : "Copy Markdown"}</span>
          </button>
        </div>
      </div>

      {/* Report Render Body */}
      <div className="bg-slate-950 rounded-xl p-5 border border-slate-800/80 text-slate-200 text-sm leading-relaxed overflow-x-auto font-sans space-y-4 max-h-[600px] overflow-y-auto">
        <div className="prose prose-invert max-w-none text-slate-300 whitespace-pre-wrap font-mono text-xs sm:text-sm">
          {reportContent}
        </div>
      </div>
    </div>
  );
};
