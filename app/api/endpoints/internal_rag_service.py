import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from mcp.types import Content, TextContent
import uvicorn

from app.rag.mcp_rag_service import KnowledgeRetrieverMCP

# 创建FastAPI应用
app = FastAPI(
    title="Knowledge Retriever API",
    description="知识检索服务 - RAG系统的检索组件",
    version="1.0.0"
)

# 初始化检索器
retriever = KnowledgeRetrieverMCP()

class RetrieveRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5

class RetrieveResponse(BaseModel):
    response: List[Content] 

@app.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_documents(request: RetrieveRequest):
    """
    检索与查询最相关的文档片段
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="查询不能为空")
        
        if request.n_results < 1 or request.n_results > 10:
            raise HTTPException(status_code=400, detail="n_results必须在1-10之间")
        
        # 执行检索
        results = retriever.retrieve(request.query, request.n_results)
        response_text = json.dumps(results, ensure_ascii=False, indent=2)
        
        return RetrieveResponse(response=[TextContent(type="text", text=response_text)])
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "knowledge-retriever"}

if __name__ == "__main__":
    uvicorn.run(
        "http_rag_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )