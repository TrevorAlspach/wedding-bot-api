from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Provider selection: "claude" or "azure_openai"
    llm_provider: str = "claude"

    # Anthropic / Claude
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"  # or claude-haiku-4-5-20251001

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-12-01-preview"
    azure_openai_chat_deployment: str = ""
    azure_openai_embedding_deployment: str = ""

    # Azure Managed Identity
    azure_client_id: str = ""  # User-assigned managed identity client ID

    # CORS
    allowed_origins: list[str] = ["http://localhost:5173"]

    # Vector store
    vectorstore_path: str = "./vectorstore"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
