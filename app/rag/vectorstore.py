import os

from langchain_community.vectorstores import FAISS
from langchain_openai import AzureOpenAIEmbeddings

from app.auth import get_azure_credential
from app.config import settings

_vectorstore: FAISS | None = None


def _build_embeddings() -> AzureOpenAIEmbeddings:
    credential = get_azure_credential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return AzureOpenAIEmbeddings(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_deployment=settings.azure_openai_embedding_deployment,
        api_version=settings.azure_openai_api_version,
        api_key=token.token,
    )


def get_vectorstore() -> FAISS:
    """Load or create the FAISS vector store."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    embeddings = _build_embeddings()
    store_path = settings.vectorstore_path

    if os.path.exists(store_path):
        _vectorstore = FAISS.load_local(
            store_path, embeddings, allow_dangerous_deserialization=True
        )
    else:
        # Bootstrap with an empty store — populate later via a seed script
        _vectorstore = FAISS.from_texts(
            ["placeholder"], embedding=embeddings
        )

    return _vectorstore


def get_retriever():
    """Return a LangChain retriever backed by the vector store."""
    return get_vectorstore().as_retriever(search_kwargs={"k": 4})
