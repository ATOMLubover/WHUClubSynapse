from typing import List, Dict, Any, Optional

from pydantic import BaseModel


# RAG 数据同步模板
class Document(BaseModel):
    document_id: int
    text: str
    metadata: Dict[str, Any]


# 聊天模板
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    user_id: Optional[int] = None
    stream: Optional[bool] = False
