import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from mcp.types import Content, TextContent
from app.utils.singleton import retriever
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="Knowledge Retriever API",
    description="知识检索服务 - RAG系统的检索组件",
    version="1.0.0"
)

# 初始化检索器

class RetrieveRequest(BaseModel):
    query: str
    n_results: Optional[int] = 5

class RetrieveResponse(BaseModel):
    response: List[Dict[str, Any]] 


class FormatRequest(BaseModel):
    retrieved_docs: List[Dict[str, Any]] 
    
class FormatResponse(BaseModel):
    response: List[TextContent]

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
        
        # 执行检索，直接返回 Python 列表
        retrieved_docs = retriever.retrieve(request.query, request.n_results)
        
        # 直接返回 Pydantic 模型，FastAPI 会自动处理 JSON 序列化
        return RetrieveResponse(response=retrieved_docs)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")

@app.post("/format", response_model=FormatResponse)
async def format_documents(retrieved_docs: FormatRequest):
    '''
    格式化检索结果为 LLM 输入
    参数:
    retrieved_docs: 检索到的文档
    '''
    context_str = "\n\n".join(
        f"""
        文档 {i + 1}:\n{doc['content']}\nMetadata: {doc['metadata']}
        """ for i, doc in enumerate(retrieved_docs)
    )
    # 直接返回 Pydantic 模型
    return FormatResponse(response=[TextContent(type="text", text=context_str)])


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