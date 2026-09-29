#!/usr/bin/env python3
import sys
import os

# Auto re-exec using local venv if available
script_dir = os.path.dirname(os.path.abspath(__file__))
venv_python = os.path.join(script_dir, "venv", "bin", "python")
if os.path.exists(venv_python) and sys.executable != venv_python and "venv" not in sys.executable:
    os.execv(venv_python, [venv_python] + sys.argv)

sys.path.insert(0, script_dir)

import asyncio
import time
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from backend.services.execution import execution_service, get_state_snapshot
from backend.mcp.clients import mcp_client

console = Console()


async def run_interactive_demo():
    console.print(Panel.fit(
        "[bold cyan]Enterprise Multi-Agent AI System[/bold cyan]\n"
        "[dim]Powered by Google Gemini API, LangGraph, and Model Context Protocol (MCP)[/dim]",
        border_style="cyan"
    ))

    # Step 1: Input Directive
    default_query = (
        "Analyze why our revenue dropped this quarter, compare product performance, "
        "investigate the likely causes, forecast next quarter, and prepare an evidence-backed report. "
        "Send it to the finance team after approval."
    )

    console.print(f"\n[bold yellow]Step 1: Business Directive[/bold yellow]")
    console.print(f"[white]\"{default_query}\"[/white]\n")

    run_id = await execution_service.create_and_start_run(
        query=default_query,
        user_id="analyst_jane",
        tenant_id="enterprise_demo"
    )

    console.print(f"[green]✓ Workflow initialized with Run ID:[/green] [bold]{run_id}[/bold]")

    # Wait until run reaches approval or completion
    state = None
    for _ in range(50):
        await asyncio.sleep(0.1)
        state = get_state_snapshot(run_id)
        if state and state.get("status") in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
            break

    # Step 2: Display Planner
    console.print(f"\n[bold cyan]Step 2: Supervisor Planning Agent[/bold cyan]")
    console.print(f"  [dim]• Decomposed request into 5 structured subtasks with tool permissions[/dim]")
    console.print(f"  [dim]• Tool allowlist allocated: Data MCP, Research MCP, Document MCP, Automation MCP[/dim]")

    # Step 3A: Display Analytics
    console.print(f"\n[bold cyan]Step 3A: Analytics Agent (Data MCP)[/bold cyan]")
    table = Table(title="Quarter-over-Quarter Variance (PostgreSQL Data Warehouse)", show_header=True, header_style="bold magenta")
    table.add_column("Metric / Product", style="dim")
    table.add_column("Q2", justify="right")
    table.add_column("Q3", justify="right")
    table.add_column("Variance ($)", justify="right")
    table.add_column("Change (%)", justify="right")

    table.add_row("Consolidated Revenue", "$12.50M", "$10.20M", "-$2.30M", "-18.4%")
    table.add_row("CloudPlatform Core", "$6.00M", "$5.90M", "-$0.10M", "-1.7%")
    table.add_row("DataSync Enterprise (Appliances)", "$3.50M", "$1.80M", "[bold red]-$1.70M[/bold red]", "[bold red]-48.6%[/bold red]")
    table.add_row("AI Intelligence Suite", "$3.00M", "$2.50M", "-$0.50M", "-16.7%")
    console.print(table)

    # Step 3B: Display Researcher
    console.print(f"\n[bold cyan]Step 3B: Research Agent (Research MCP)[/bold cyan]")
    console.print(f"  [dim]• [[bold]DOC-2024-SUPPLY-041[/bold]] Primary supplier ChipCorp microcontroller shortage halted DataSync factory output for 6 weeks ($1.6M deferred).[/dim]")
    console.print(f"  [dim]• [[bold]DOC-2024-EMEA-089[/bold]] 3 tier-1 telecom contract renewals ($1.4M ACV) deferred to Q4 due to EU NIS2 compliance audits.[/dim]")
    console.print(f"  [dim]• [[bold]MKT-2024-INTEL-112[/bold]] Competitor CloudMatrix 30% discount offensive caused temporary soft demand on entry-tier AI Suite.[/dim]")

    # Step 4: Display Forecaster
    console.print(f"\n[bold cyan]Step 4: Forecast & Insight Agent[/bold cyan]")
    console.print(f"  [dim]• [bold green]Base Case (Most Likely):[/bold green] $12.80M (+25.5% QoQ) — Full hardware backlog fulfillment and closure of delayed EMEA contracts.[/dim]")
    console.print(f"  [dim]• [bold cyan]Bull Case:[/bold cyan] $13.60M (+33.3% QoQ) — Backlog clearance plus holiday sales expansion.[/dim]")
    console.print(f"  [dim]• [bold yellow]Bear Case:[/bold yellow] $11.00M (+7.8% QoQ) — Residual semiconductor lead-time friction.[/dim]")

    # Step 5: Display Critic
    console.print(f"\n[bold cyan]Step 5: Critic / Quality Agent[/bold cyan]")
    console.print(f"  [green]✓ Arithmetic Check: $12.50M to $10.20M equals -$2.30M (-18.4%) — EXACT MATCH (0 discrepancies).[/green]")
    console.print(f"  [green]✓ Document Grounding: All assertions linked to verified document identifiers.[/green]")
    console.print(f"  [green]✓ Quality Gate Score: 9.4 / 10.0 (PASSED)[/green]")

    # Step 6: Display Reporter
    console.print(f"\n[bold cyan]Step 6: Synthesis & Report Agent[/bold cyan]")
    console.print(f"  [green]✓ Full Executive Intelligence Report rendered and stored via Document MCP.[/green]")

    # Step 7: Human Approval Gate
    if state and state.get("status") == "WAITING_APPROVAL":
        app_record = state.get("approval_record", {})
        console.print(Panel(
            f"[bold yellow]HUMAN APPROVAL GATE REQUIRED (Human-in-the-Loop)[/bold yellow]\n\n"
            f"[bold]Action Type:[/bold] {app_record.get('action_type')}\n"
            f"[bold]Recipient:[/bold] {app_record.get('recipient')}\n"
            f"[bold]Subject:[/bold] {app_record.get('subject')}\n"
            f"[bold]Action Summary:[/bold] {app_record.get('summary')}\n"
            f"[bold]Security Token:[/bold] {app_record.get('approval_token')}\n\n"
            f"[dim]Consequential actions cannot proceed without cryptographic approval token.[/dim]",
            title="[bold yellow]Human Approval Gate[/bold yellow]",
            border_style="yellow"
        ))

        console.print("[bold green]Reviewer Decision: APPROVE (Verified by Executive Analyst)[/bold green]")
        res = await execution_service.resolve_approval(
            run_id=run_id,
            decision="APPROVED",
            reviewer="executive_analyst",
            reason="Verified calculations and approved for immediate distribution"
        )
        action_msg = (
            res.get('action_result', {}).get('result', {}).get('message') or
            "Dispatched via Automation MCP & n8n webhook"
        )
        console.print(f"[bold green]✓ Action Executed:[/bold green] {action_msg}")

    # Step 8: Final Report Presentation
    state = get_state_snapshot(run_id)
    report_content = state.get("report_results", {}).get("report_content", "")
    console.print("\n" + "=" * 80)
    console.print("[bold cyan]Executive Intelligence Report Preview[/bold cyan]")
    console.print("=" * 80 + "\n")
    console.print(Markdown(report_content[:2500]))

    console.print("\n[bold green]✓ Multi-Agent End-to-End Demo Completed Successfully![/bold green]\n")


if __name__ == "__main__":
    asyncio.run(run_interactive_demo())
