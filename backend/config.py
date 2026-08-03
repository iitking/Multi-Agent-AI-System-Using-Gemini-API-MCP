import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Gemini Configuration
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    GEMINI_FALLBACK_TO_MOCK: bool = Field(default=True, description="Fallback to mock responses if API key is not provided")

    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Backend host")
    PORT: int = Field(default=8000, description="Backend port")
    ENVIRONMENT: str = Field(default="development", description="Environment: development, production, test")
    LOG_LEVEL: str = Field(default="INFO", description="Log level")
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000", description="Comma separated origins")

    # Security & Auth
    JWT_SECRET: str = Field(default="super-secret-jwt-key-multi-agent-system-2025", description="JWT secret key")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="Token expiration minutes")

    # Database
    DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./multi_agent_system.db", description="Database connection URL")

    # LangSmith Observability
    LANGSMITH_TRACING: bool = Field(default=False, description="Enable LangSmith tracing")
    LANGSMITH_ENDPOINT: str = Field(default="https://api.smith.langchain.com", description="LangSmith endpoint")
    LANGSMITH_API_KEY: str = Field(default="", description="LangSmith API key")
    LANGSMITH_PROJECT: str = Field(default="enterprise-gemini-multi-agent", description="LangSmith project")

    # n8n Integration
    N8N_WEBHOOK_URL: str = Field(default="http://localhost:5678/webhook/finance-approval", description="n8n webhook URL")
    N8N_ENABLED: bool = Field(default=True, description="Enable n8n workflow triggers")
    N8N_WEBHOOK_SECRET: str = Field(default="n8n-enterprise-secret-key-9988", description="n8n shared secret")

    # Multi-Agent Workflow Budget & Limits
    MAX_RETRY_COUNT: int = Field(default=2, description="Maximum critic retry count")
    MAX_TOOL_CALL_BUDGET: int = Field(default=25, description="Max tool calls per run")
    MAX_EXECUTION_TIME_SECONDS: int = Field(default=180, description="Run timeout in seconds")
    MAX_TOKEN_BUDGET: int = Field(default=50000, description="Token limit per workflow run")

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()
