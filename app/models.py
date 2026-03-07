from pydantic import BaseModel


class MessagePayload(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[MessagePayload]
