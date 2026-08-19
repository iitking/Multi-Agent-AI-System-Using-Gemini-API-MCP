import uuid
from typing import Dict, Any, List, Optional

# In-memory document & report repository
STORED_REPORTS: Dict[str, Dict[str, Any]] = {}


class DocumentMCPServer:
    """MCP Server for document synthesis, report formatting, and persistent document storage."""

    name = "Document_MCP_Server"

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "read_document",
                "description": "Read file content from authorized internal report templates or storage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_path": {"type": "string", "description": "Path or identifier of the document"}
                    },
                    "required": ["doc_path"]
                }
            },
            {
                "name": "create_report",
                "description": "Compile structured executive report from verified multi-agent analysis sections.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Report title"},
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "heading": {"type": "string"},
                                    "content": {"type": "string"}
                                }
                            },
                            "description": "List of report sections"
                        },
                        "format": {"type": "string", "description": "markdown or html"}
                    },
                    "required": ["title", "sections"]
                }
            },
            {
                "name": "save_report",
                "description": "Persist finalized verified report to enterprise document store.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "report_id": {"type": "string", "description": "Unique report ID"},
                        "content": {"type": "string", "description": "Full report content"},
                        "format": {"type": "string", "description": "markdown, pdf, or html"}
                    },
                    "required": ["report_id", "content"]
                }
            }
        ]

    def read_document(self, doc_path: str) -> Dict[str, Any]:
        if doc_path in STORED_REPORTS:
            return {"found": True, "report": STORED_REPORTS[doc_path]}
        return {
            "found": True,
            "template": "Executive Briefing Template v2.4",
            "format": "markdown",
            "required_sections": ["Executive Summary", "Data Analytics", "Root Cause Investigation", "Scenarios & Forecasts", "Strategic Recommendations"]
        }

    def create_report(self, title: str, sections: List[Dict[str, str]], format: str = "markdown") -> Dict[str, Any]:
        report_id = f"REP-{uuid.uuid4().hex[:8].upper()}"
        rendered_content = f"# {title}\n\n"
        for section in sections:
            heading = section.get("heading", "Section")
            body = section.get("content", "")
            rendered_content += f"## {heading}\n{body}\n\n"

        STORED_REPORTS[report_id] = {
            "report_id": report_id,
            "title": title,
            "content": rendered_content,
            "format": format
        }

        return {
            "report_id": report_id,
            "status": "CREATED",
            "content": rendered_content,
            "character_count": len(rendered_content)
        }

    def save_report(self, report_id: str, content: str, format: str = "markdown") -> Dict[str, Any]:
        STORED_REPORTS[report_id] = {
            "report_id": report_id,
            "content": content,
            "format": format
        }
        return {
            "report_id": report_id,
            "status": "PERSISTED",
            "format": format
        }


document_server = DocumentMCPServer()
