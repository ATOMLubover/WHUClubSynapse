from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field


# RAG 数据同步模板
class Document(BaseModel):
    document_id: int
    text: str
    metadata: Dict[str, Any]


# 聊天模板
class ChatMessage(BaseModel):
    """单条聊天消息的模型"""
    role: str = Field(..., description="消息发送者的角色，必须是 'user' 或 'assistant'")
    content: str = Field(..., description="消息的具体内容")

class ChatQuery(BaseModel):
    """聊天请求的模型"""
    query: str = Field(..., description="用户的最新一条消息")
    history: List[ChatMessage] = Field([], description="历史对话记录，由前端负责维护和传递")  # TODO: 真的由前端吗

class ChatResponse(BaseModel):
    """聊天响应的模型，结构与SearchResponse相同"""
    answer: str = Field(..., description="模型生成的答案")
    source: List[Dict[str, Any]] = Field(..., description="答案的溯源文档列表")
    stream: Optional[bool] = False


# 查询（或者说搜索）模板
class SearchQuery(BaseModel):
    query: str

class SearchResponse(BaseModel):
    answer: str = Field(..., description="AI智能搜索总结")
    source: List[Dict[str, Any]] = Field(..., description="来源")