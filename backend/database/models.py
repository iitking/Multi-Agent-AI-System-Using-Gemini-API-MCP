import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="analyst")  # admin, analyst, viewer
    tenant_id: Mapped[str] = mapped_column(String(50), default="default_tenant", index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RunRecord(Base):
    __tablename__ = "run_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), default="anonymous")
    tenant_id: Mapped[str] = mapped_column(String(50), default="default_tenant", index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)  # PENDING, RUNNING, WAITING_APPROVAL, COMPLETED, FAILED, ESCALATED
    plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    state_snapshot: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_cost: Mapped[float] = mapped_column(Float, default=0.0)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    steps = relationship("TaskStep", back_populates="run", cascade="all, delete-orphan")
    audit_logs = relationship("ToolAuditLog", back_populates="run", cascade="all, delete-orphan")
    approvals = relationship("ApprovalRecord", back_populates="run", cascade="all, delete-orphan")
    reports = relationship("FinalReport", back_populates="run", cascade="all, delete-orphan")


class TaskStep(Base):
    __tablename__ = "task_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("run_records.id"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    step_type: Mapped[str] = mapped_column(String(100), default="agent_execution")
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED")
    input_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    output_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run = relationship("RunRecord", back_populates="steps")


class ToolAuditLog(Base):
    __tablename__ = "tool_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("run_records.id"), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    server_name: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    arguments: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="SUCCESS")  # SUCCESS, DENIED, ERROR
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    tenant_id: Mapped[str] = mapped_column(String(50), default="default_tenant")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run = relationship("RunRecord", back_populates="audit_logs")


class ApprovalRecord(Base):
    __tablename__ = "approval_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("run_records.id"), nullable=False, index=True)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)  # send_email, slack_notification, crm_task
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED
    approval_token: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    approved_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    run = relationship("RunRecord", back_populates="approvals")


class FinalReport(Base):
    __tablename__ = "final_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("run_records.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    format: Mapped[str] = mapped_column(String(50), default="markdown")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    run = relationship("RunRecord", back_populates="reports")


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
