from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType, VectorizableTextQuery
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.config import settings


def _build_search_client() -> SearchClient:
    return SearchClient(
        endpoint=settings.azure_search_endpoint,
        index_name=settings.azure_search_index,
        credential=AzureKeyCredential(settings.azure_search_api_key),
    )


class AzureAISearchRetriever(BaseRetriever):
    """Hybrid retriever using Azure AI Search (vector + BM25 + semantic ranker)."""

    search_client: SearchClient
    top_k: int = 4

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str, **kwargs) -> list[Document]:
        results = self.search_client.search(
            search_text=query,
            vector_queries=[
                VectorizableTextQuery(
                    text=query,
                    k_nearest_neighbors=self.top_k,
                    fields="content_vector",
                )
            ],
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name="default",
            top=self.top_k,
        )
        return [
            Document(
                page_content=r["content"],
                metadata={"score": r["@search.score"]},
            )
            for r in results
        ]


def get_retriever() -> AzureAISearchRetriever:
    """Return a hybrid retriever backed by Azure AI Search."""
    return AzureAISearchRetriever(
        search_client=_build_search_client(),
        top_k=4,
    )
