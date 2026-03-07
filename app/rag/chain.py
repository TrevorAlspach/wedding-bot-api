from collections.abc import AsyncIterator

from langchain_core.messages import AIMessageChunk, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import AzureChatOpenAI

from app.auth import get_azure_credential
from app.config import settings
from app.models import MessagePayload
from app.rag.vectorstore import get_retriever

SYSTEM_PROMPT = """\
You are a helpful wedding assistant for Trev & Lin's wedding.
Use the following retrieved context to answer questions about the wedding.
If you don't know the answer, say so — do not make up information.

Context:
{context}
"""


def _build_llm() -> AzureChatOpenAI:
    credential = get_azure_credential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return AzureChatOpenAI(
        azure_endpoint=settings.azure_openai_endpoint,
        azure_deployment=settings.azure_openai_chat_deployment,
        api_version=settings.azure_openai_api_version,
        api_key=token.token,
        streaming=True,
    )


def _to_langchain_messages(
    messages: list[MessagePayload], context: str
) -> list[BaseMessage]:
    lc_messages: list[BaseMessage] = [
        SystemMessage(content=SYSTEM_PROMPT.format(context=context)),
    ]
    for m in messages:
        if m.role == "user":
            lc_messages.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            lc_messages.append(AIMessageChunk(content=m.content))
    return lc_messages


async def stream_rag_response(
    messages: list[MessagePayload],
) -> AsyncIterator[str]:
    """Run RAG retrieval then stream the LLM response as SSE events."""
    # Use the last user message for retrieval
    last_user_msg = next(
        (m.content for m in reversed(messages) if m.role == "user"), ""
    )

    retriever = get_retriever()
    docs = retriever.invoke(last_user_msg)
    context = "\n\n".join(doc.page_content for doc in docs)

    llm = _build_llm()
    lc_messages = _to_langchain_messages(messages, context)

    async for chunk in llm.astream(lc_messages):
        if chunk.content:
            yield chunk.content
