import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models import ChatRequest
from app.rag.chain import stream_rag_response

router = APIRouter()


async def _event_stream(request: ChatRequest) -> AsyncGenerator[str, None]:
    try:
        async for token in stream_rag_response(request.messages):
            payload = json.dumps({"type": "text", "content": token})
            yield f"data: {payload}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as exc:
        payload = json.dumps({"type": "error", "content": str(exc)})
        yield f"data: {payload}\n\n"
        yield "data: [DONE]\n\n"


@router.post("/api/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        _event_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
