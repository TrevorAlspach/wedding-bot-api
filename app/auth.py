from azure.identity import DefaultAzureCredential, ManagedIdentityCredential

from app.config import settings


def get_azure_credential():
    """Return an Azure credential.

    In production (Azure), uses the user-assigned managed identity.
    Locally, DefaultAzureCredential falls through to Azure CLI / env-var creds.
    """
    if settings.azure_client_id:
        return ManagedIdentityCredential(client_id=settings.azure_client_id)
    return DefaultAzureCredential()
