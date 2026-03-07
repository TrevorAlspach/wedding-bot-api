from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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
