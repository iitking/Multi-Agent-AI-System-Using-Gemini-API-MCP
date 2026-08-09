from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def add(self, other: "TokenUsage"):
        self.prompt_tokens += other.prompt_tokens
        self.completion_tokens += other.completion_tokens
        self.total_tokens += other.total_tokens
        self.estimated_cost_usd += other.estimated_cost_usd


@dataclass
class LLMResponse:
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    model_name: str = "gemini-2.5-flash"
    finish_reason: str = "stop"
