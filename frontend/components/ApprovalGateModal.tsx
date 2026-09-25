"use client";

import React, { useState } from "react";
import { ShieldAlert, CheckCircle, XCircle, Mail, AlertTriangle } from "lucide-react";
import { ApprovalRecord } from "../lib/types";

interface ApprovalGateModalProps {
  isOpen: boolean;
  onClose: () => void;
  approvalRecord?: ApprovalRecord;
  onApprove: (comment: string) => Promise<void>;
  onReject: (reason: string) => Promise<void>;
  runId: string;
}

export const ApprovalGateModal: React.FC<ApprovalGateModalProps> = ({
  isOpen,
  onClose,
  approvalRecord,
  onApprove,
  onReject,
  runId,
}) => {
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen || !approvalRecord) return null;

  const handleApprove = async () => {
    setIsSubmitting(true);
    try {
      await onApprove(comment);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReject = async () => {
    setIsSubmitting(true);
    try {
      await onReject(comment);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-5">
        <div className="flex items-start space-x-3">
          <div className="h-10 w-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center flex-shrink-0">
            <ShieldAlert className="h-5 w-5 text-amber-400" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-white">Human Approval Gate Required</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              A consequential external action has been flagged by the Synthesis Agent. Review and authorize before execution.
            </p>
          </div>
        </div>

        {/* Action Details Card */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 space-y-3 text-sm">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <span className="text-xs text-slate-400 font-mono">ACTION TYPE:</span>
            <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-mono text-xs font-semibold">
              {approvalRecord.action_type}
            </span>
          </div>

          <div>
            <span className="text-xs text-slate-400 block mb-1">RECIPIENT & SUBJECT:</span>
            <p className="text-slate-200 font-medium">{approvalRecord.recipient || "Executive Finance Team"}</p>
            <p className="text-xs text-slate-400 italic mt-0.5">{approvalRecord.subject}</p>
          </div>

          <div>
            <span className="text-xs text-slate-400 block mb-1">PROPOSED ACTION SUMMARY:</span>
            <p className="text-slate-300 text-xs bg-slate-900 p-2.5 rounded-lg border border-slate-800">
              {approvalRecord.summary}
            </p>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-slate-800 text-xs">
            <span className="text-slate-500 font-mono">SECURITY TOKEN:</span>
            <span className="font-mono text-emerald-400">{approvalRecord.approval_token}</span>
          </div>
        </div>

        {/* Reviewer Comment Input */}
        <div>
          <label className="text-xs text-slate-400 font-medium block mb-1">
            Reviewer Audit Comment / Justification:
          </label>
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="e.g. 'Calculations verified against ERP ledger. Authorized.'"
            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end space-x-3 pt-2">
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            Cancel
          </button>

          <button
            onClick={handleReject}
            disabled={isSubmitting}
            className="px-4 py-2 rounded-lg text-xs font-semibold bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center space-x-1.5 transition-all"
          >
            <XCircle className="h-4 w-4" />
            <span>Reject Action</span>
          </button>

          <button
            onClick={handleApprove}
            disabled={isSubmitting}
            className="px-5 py-2 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-600/30 flex items-center space-x-1.5 transition-all"
          >
            <CheckCircle className="h-4 w-4" />
            <span>Approve & Trigger Automation</span>
          </button>
        </div>
      </div>
    </div>
  );
};
