# Enterprise Multi-Agent AI System Using Gemini API + MCP

An advanced, enterprise-oriented AI operations and intelligence platform built with the **Gemini API**, **LangGraph**, **Model Context Protocol (MCP)**, **LangSmith**, and **n8n**.

The system accepts complex business requests, decomposes them into tasks, coordinates specialized agents, retrieves authorized data through MCP tools, validates evidence, generates reports, and routes consequential actions through human approval.

---

##  Project Overview


The system can:

1. Break the request into dependent subtasks.
2. Analyze company data using authorized database tools.
3. Research relevant internal documents and approved external sources.
4. Identify trends and anomalies and forecast scenarios.
5. Verify calculations and citations before accepting results.
6. Generate a business report with recommendations and confidence indicators.
7. Request human approval before sending the report or triggering business actions.
8. Record agent decisions, tool calls, latency, failures, and cost.

**Core design principle:** Gemini provides reasoning and generation capabilities, LangGraph controls the multi-agent workflow, and MCP provides standardized access to tools and data.

##  Project Goals

- Coordinate specialized AI agents on complex business tasks.
- Use MCP as a standardized interface to tools and data sources.
- Use LangGraph for stateful orchestration and conditional routing.
- Use LangSmith for tracing, debugging, and evaluation.
- Use n8n to trigger external business workflows.
- Provide a dashboard for requests, execution status, reports, and approvals.
- Apply authentication, authorization, validation, and audit logging.
- Measure quality, latency, reliability, and cost.

---

##  Advanced System Architecture

```mermaid
flowchart TD
    U["User / Business Team"] --> FE["Next.js Dashboard<br/>Chat · Analytics · Run History · Approvals"]
    FE --> API["FastAPI API Gateway<br/>Authentication · RBAC · Tenant Isolation · Validation"]
    API --> LG["LangGraph Orchestrator<br/>Persistent State · Checkpoints · Routing · Recovery"]

    LG --> P["Supervisor / Planning Agent"]
    P --> DA["Analytics Agent"]
    P --> RA["Research Agent"]
    DA --> IA["Forecast & Insight Agent"]
    RA --> IA
    IA --> QA["Critic / Quality Agent"]
    QA --> QC{"Quality Check Passed?"}
    QC -- "No: bounded retry" --> IA
    QC -- "No: retries exhausted" --> PARTIAL["Escalate / Partial Result"]
    QC -- "Yes" --> RG["Synthesis & Report Agent"]
    RG --> ACTION{"External Action Needed?"}
    ACTION -- "Yes" --> HUMAN["Human Approval Gate"]
    HUMAN -- "Approved" --> N8N["n8n / Approved MCP Action"]
    HUMAN -- "Rejected" --> REJECT["Record Rejection"]
    ACTION -- "No" --> OUT["Persist Final Report"]
    N8N --> OUT
    OUT --> DASH["Dashboard + Audit Trail"]
    PARTIAL --> DASH
    REJECT --> DASH

    DA -. "MCP client" .-> MCPD["Data MCP Server"]
    RA -. "MCP client" .-> MCPR["Research MCP Server"]
    RG -. "MCP client" .-> MCPF["Document MCP Server"]
    N8N -. "workflow integration" .-> MCPX["Approved Business Tools"]

    MCPD --> DB["PostgreSQL / Approved Data"]
    MCPR --> DOCS["Approved Search / Company Documents"]
    MCPF --> OBJ["Object Storage / Generated Reports"]

    LG -. "traces and evaluations" .-> LS["LangSmith"]
    API --> OBS["OpenTelemetry / Logs / Metrics"]
    LG --> CACHE["Redis / Durable Task Queue (optional)"]
```

### Responsibilities

- **Frontend:** Request submission, run status, reports, and human approvals.
- **FastAPI:** API endpoints, validation, authentication, authorization, and rate limiting.
- **LangGraph:** Agent coordination, shared workflow state, branching, retries, and checkpoints.
- **Gemini API:** Language-model inference, planning, reasoning, and structured generation.
- **MCP clients and servers:** Standardized discovery and invocation of approved tools and resources.
- **n8n:** Scheduled workflows and integrations such as email, Slack, or CRM tasks.
- **PostgreSQL:** Application data, users, projects, workflow metadata, and results.
- **Redis / background worker:** Optional caching and asynchronous task processing.
- **LangSmith and OpenTelemetry:** Tracing, evaluation, latency, and debugging.
- **Object storage:** Uploaded files and generated reports.

### Important architecture distinctions

- **Gemini API** provides model inference; it does not replace your workflow engine or database.
- **LangGraph** controls which agent runs next, what state it receives, and how failures or approvals are handled.
- **MCP** standardizes tool access; each MCP server must still enforce its own permissions.
- **n8n** handles integrations and external business workflows; it is not the primary reasoning engine.
- **LangSmith** supports tracing and evaluation; it is not a security boundary.
- **Policy enforcement** checks whether an agent is allowed to call a tool before execution.

---

##  Recommended Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | Gemini API via `google-genai` | Reasoning, summarization, structured responses |
| Orchestration | LangGraph | Stateful workflows, branching, retries, approvals |
| Agent tools | MCP Python SDK | Standardized access to custom and external tools |
| Backend | FastAPI + Pydantic | Secure APIs and schema validation |
| Frontend | Next.js + TypeScript | Enterprise dashboard |
| Workflow automation | n8n | CRM, email, Slack, scheduled operations |
| Primary database | PostgreSQL | Business data, users, tasks, audit metadata |
| Vector search | pgvector (optional) | Retrieval over company documents |
| Background jobs | Redis + Celery or an equivalent worker | Long-running jobs and asynchronous processing |
| Tracing | LangSmith + OpenTelemetry | Execution traces, debugging, latency analysis |
| Testing | pytest + agent evaluation datasets | Regression tests and quality measurement |
| Deployment | Docker + cloud infrastructure | Reproducible builds and deployment |
| Security | OAuth/OIDC + RBAC + policy checks | Authentication, permissions, controlled execution |

Use Google's official [Gen AI SDK for Python](https://googleapis.github.io/python-genai/) for Gemini API integration. For new projects, avoid starting with the legacy `google-generativeai` Python package.

Configure the Gemini model name using environment variables rather than hardcoding it throughout the codebase. Select a model based on current availability, quality tests, latency, and cost.

### Recommended initial deployment

Start with:

- Python
- FastAPI
- Gemini API via `google-genai`
- LangGraph
- MCP Python SDK
- PostgreSQL
- LangSmith
- Docker

Add Next.js and n8n as the product and workflow needs become clear. Kubernetes, Kafka, and a separate deployed service for every agent are not mandatory for the first implementation.

---

##  Multi-Agent Design

Use a **supervisor-and-specialists architecture**. The supervisor manages the workflow, while specialized agents handle focused jobs.

| Agent | Responsibility | Example output |
|---|---|---|
| Supervisor / Planner | Understands the request and creates a structured plan | Tasks, dependencies, permitted tools |
| Analytics Agent | Queries approved datasets and calculates metrics | Revenue, growth, product rankings |
| Research Agent | Retrieves approved supporting context | Findings and source references |
| Forecast & Insight Agent | Interprets evidence and estimates scenarios | Findings, forecasts, assumptions |
| Critic / Quality Agent | Checks evidence, arithmetic, and completeness | Pass/fail decision and issues |
| Synthesis & Report Agent | Creates the final report | Markdown, HTML, or PDF report |

Agents should return structured outputs with explicit fields such as `status`, `findings`, `evidence`, `errors`, and `next_action`. Prefer compact result objects over passing large, unstructured conversation histories between agents.

### Agent responsibilities in detail

#### 1. Supervisor / Planner Agent
- Breaks a complex request into a task plan.
- Identifies dependencies and tasks that can run in parallel.
- Selects appropriate agents and permitted tools.
- Applies task limits and respects the system's authorization policies.

#### 2. Analytics Agent
- Queries approved data through MCP tools.
- Calculates KPIs and compares reporting periods.
- Detects anomalies and identifies data-quality issues.
- Returns the figures, definitions, and data provenance.

#### 3. Research Agent
- Searches approved company documents and external sources.
- Retrieves relevant evidence.
- Returns source identifiers, timestamps when available, and relevance assessments.

#### 4. Forecast & Insight Agent
- Combines validated business metrics with retrieved evidence.
- Uses statistical models for forecasting and scenario analysis.
- Separates measured facts from hypotheses and assumptions.

#### 5. Critic / Quality Agent
- Checks calculations, evidence, schema validity, and completeness.
- Identifies unsupported claims or conflicting sources.
- Requests bounded retries or escalates unresolved issues.

#### 6. Synthesis & Report Agent
- Produces an evidence-backed report.
- Includes findings, assumptions, recommendations, limitations, and next actions.
- Cannot bypass tool permissions or approval requirements.

Use Python libraries for numerical calculations rather than relying on the language model to perform important arithmetic from memory.

---

## 6. How Gemini API and MCP Work Together

Gemini function calling allows a model to request a tool operation. Your application validates and executes that operation, then returns the result to the model. MCP provides a standardized way for your application to discover and invoke tools exposed by MCP servers. These mechanisms are related but distinct.

### Recommended execution flow

1. FastAPI receives and validates the business request.
2. LangGraph invokes the planner using Gemini.
3. The planner returns a validated task plan.
4. LangGraph routes tasks to the analytics and research agents.
5. Each agent uses an MCP client to discover permitted tools on the relevant MCP server.
6. The application validates permissions and arguments before executing a tool.
7. Results return as structured data with provenance where possible.
8. The insight and critic agents examine the evidence.
9. LangGraph routes the workflow to a retry, approval, or report node.
10. The application stores the outcome and exposes the run trace to authorized users.

**Security rule:** Never execute a privileged operation just because a model generated its tool name or arguments. Validate the requested tool against an allowlist and enforce authorization independently of the prompt.

### Example MCP servers and tools

| MCP server | Example tools | Purpose |
|---|---|---|
| Data MCP Server | `get_sales_summary`, `query_readonly_database`, `calculate_kpis` | Controlled business analytics |
| Research MCP Server | `search_approved_sources`, `search_company_docs` | Evidence retrieval |
| Document MCP Server | `read_document`, `create_report`, `save_report` | Document processing |
| Automation MCP Server | `send_approved_email`, `notify_slack`, `create_crm_task` | Approved business actions |

MCP supports tools, resources, and prompts. For example, a data server can expose database schema information as a resource, and reusable analysis instructions can be exposed as prompts.

### MCP and n8n

n8n can provide workflow automation and external integrations. Depending on the n8n version and deployment, its MCP Client Tool node can connect an AI workflow to external MCP tools, and its MCP Server Trigger can expose selected workflow functionality to external MCP clients. Confirm the relevant node behavior in the version you deploy.

---

##  Advanced Workflow

```mermaid
flowchart TD
    A["Business Request"] --> B["FastAPI Authentication and Validation"]
    B --> C["Create Run and Checkpoint"]
    C --> D["Gemini Planner"]
    D --> E["Validate Structured Task Plan"]
    E --> F["LangGraph Supervisor"]

    F --> G["Analytics Agent"]
    F --> H["Research Agent"]

    G --> I["Authorized MCP Data Tools"]
    H --> J["Authorized MCP Research Tools"]

    I --> K["Normalize and Validate Evidence"]
    J --> K

    K --> L["Insight and Forecast Agent"]
    L --> M["Critic / QA Agent"]
    M --> N{"Quality Passed?"}

    N -- "No, retries remain" --> L
    N -- "No, retries exhausted" --> O["Escalate / Partial Result"]
    N -- "Yes" --> P["Report Agent"]

    P --> Q{"External Action?"}
    Q -- "Yes" --> R["Human Approval Gate"]
    R -- "Rejected" --> S["Record Rejection"]
    R -- "Approved" --> T["n8n / Approved MCP Action"]
    Q -- "No" --> U["Persist Final Report"]
    T --> U

    U --> V["Dashboard and Audit Trail"]
    O --> V
    S --> V

    C -.-> W["LangSmith Tracing"]
    F -.-> W
    I -.-> X["Tool Audit Logs"]
    J -.-> X
```

### Reliability controls

- Persistent workflow state and recovery after interruption.
- Parallel execution for independent tasks.
- Explicit dependencies between tasks.
- Typed agent outputs with validation.
- Bounded retries and failure escalation.
- Evidence provenance and reproducible calculations.
- Human approval before consequential actions.
- Per-user and per-tenant permissions.
- End-to-end tracing and evaluation.
- Cost, latency, and execution budgets.

Avoid unrestricted agent loops. Set maximum iterations, execution deadlines, tool-call budgets, and model-token limits for each run.

---

##  Suggested GitHub Repository Structure

```text
enterprise-gemini-multi-agent/
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── routes.py
│   │   ├── auth.py
│   │   └── approvals.py
│   ├── agents/
│   │   ├── planner.py
│   │   ├── analytics.py
│   │   ├── researcher.py
│   │   ├── forecaster.py
│   │   ├── critic.py
│   │   └── reporter.py
│   ├── graph/
│   │   ├── state.py
│   │   ├── workflow.py
│   │   ├── routing.py
│   │   └── checkpoints.py
│   ├── llm/
│   │   ├── gemini_client.py
│   │   └── model_config.py
│   ├── mcp/
│   │   ├── clients.py
│   │   ├── permissions.py
│   │   └── servers/
│   │       ├── data_server.py
│   │       ├── research_server.py
│   │       └── document_server.py
│   ├── policy/
│   ├── database/
│   ├── services/
│   └── evaluation/
├── n8n/
│   └── workflows/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── security/
│   └── evaluations/
├── infra/
│   ├── docker/
│   └── deployment/
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

This is a logical starting structure. Initially, run the backend and a small number of MCP servers locally or in a controlled deployment. Split services into separate deployments when isolation, scaling, or operational needs justify it.

---

##  Official Documentation

- [Gemini API documentation](https://ai.google.dev/gemini-api/docs)
- [Google Gen AI SDK for Python](https://googleapis.github.io/python-genai/)
- [Gemini function calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Gemini structured outputs](https://ai.google.dev/gemini-api/docs/structured-output)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [LangGraph documentation](https://docs.langchain.com/oss/python/langgraph/overview)
- [LangSmith documentation](https://docs.langchain.com/langsmith/home)
- [n8n documentation](https://docs.n8n.io/)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL documentation](https://www.postgresql.org/docs/)
- [Docker documentation](https://docs.docker.com/)

---

## Final Recommendation

Build an **Enterprise AI Operations & Intelligence Platform** using the Gemini API, LangGraph, MCP, LangSmith, and n8n.

Start with one complete use case:

**Business question → Task plan → Read-only MCP tools → Verified insights → Report**

Then expand into advanced orchestration, human approvals, forecasting, enterprise authentication, and automation.

The engineering achievement is not the number of agents. It is a reliable, secure, measurable system that produces useful business outcomes.

---

## 👨‍💻 Author

<div align="center">

<a href="https://github.com/iitking">
  <img src="https://github.com/iitking.png" width="110" height="110" style="border-radius:50%" alt="Nivesh Kumar Meena" />
</a>

### **Nivesh Kumar Meena**

**AI Architect · MLOps Engineer** | B.Tech Electrical Engineering, **IIT Roorkee**

*Building agentic AI systems, RAG pipelines and production-ready ML.*

<a href="https://www.linkedin.com/in/nivesh-kumar-meena-a31465221/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
<a href="https://github.com/iitking"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="mailto:niveshkr149@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>

<br/><br/>

⭐ **If you found this project useful, please give it a star!** ⭐

<sub>Open to AI/ML engineering opportunities and collaborations.</sub>

</div>

---

<div align="center">
  <sub>Made with ❤️ by <a href="https://github.com/iitking">Nivesh Kumar Meena</a> · © 2026 · MIT License</sub>
</div>

