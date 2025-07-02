import httpx
import re
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse
from app.utils.auth import get_api_key
from app.configs.config import settings
from app.rag.rag_service import retrieve, format_context
from app.schemas import SearchQuery, SearchResponse
from app.utils.singleton import logger

# 创建 FastAPI 路由，通过 dependencies 参数应用认证
router = APIRouter(
    dependencies=[Depends(get_api_key)]
)

@router.get("/smart-search", summary="AI智能搜索总结接口测试")
def test_smart_search():
    return "smart-search 接口的 GET 请求成功了！"


@router.post("/smart-search", summary="AI智能搜素总结接口")
async def smart_search(search_query: SearchQuery):
    """
    接收用户查询，通过 RAG 增强后调用大模型，以流式响应返回最终总结及溯源信息。
    """
    user_query = search_query.query
    if not user_query:
        raise HTTPException(status_code=400, detail="没有收到查询内容")
    logger.info(f"收到新的智能搜索请求, 查询: '{user_query}'")
    # 1. 先同步执行 RAG 检索，因为溯源信息需要先于回答返回
    try:
        # 1. 调用 RAG 服务，进行文档检索
        retrieved_docs = await run_in_threadpool(retrieve, query=user_query, n_results=settings.RAG_N_RESULT)
        logger.info(f"检索到 {len(retrieved_docs)} 篇相关文档")
        context_str = format_context(retrieved_docs=retrieved_docs)
    except Exception as e:
        logger.error(f"RAG 检索或格式化失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"检索相关文档时出错: {str(e)}")

    # 2. 构建增强提示
    final_prompt = f"""
    你是一个“社团管理系统”的AI助手。你的核心任务是为用户提供清晰、准确、有用的信息。

    **用户提问：**
    {user_query}

    **参考上下文：**
    {context_str}

    ---
    **你的任务指示：**

    1.  **优先处理上下文**：请优先使用上面提供的“参考上下文”来回答与社团管理系统功能（如创建社团、发布活动、帖子等）相关的问题。
    2.  **切换通用知识**：如果上下文信息不足，或者用户提问与社团系统完全无关（例如，“什么是光合作用？”），请直接利用你的通用知识库来生成一个全面的概览。
    3.  **保持结构化输出**：无论回答哪类问题，都请尽量遵循以下结构：
        *   **核心摘要**：首先，用一两句话直接给出最核心的答案或定义。
        *   **关键信息/步骤**：然后，分点列出关键的细节、操作步骤或相关概念。
        *   **实用技巧/补充**：最后，提供一些相关的实用技巧、注意事项或补充信息。
    4. **回答中不要给出具体参考哪个文档**：在回答中不要给出具体参考哪个文档来源的提示，这部分已经由RAG系统给出。
    5. **保持可读性**：保持总结对人类用户的可读性，避免过度分点和缩句。

    请使用 Markdown 格式化你的回答，确保内容友好、易于理解。
    """
    logger.debug(f"构建的最终提示 (前300字符): {final_prompt[:300]}...")

    # 3. 定义一个异步生成器，用于流式处理
    async def stream_generator():
        # a. 通过 SSE 发送溯源文档事件
        # logger.debug(f"retrieved_docs: {type(retrieved_docs[0])}")
        yield f"event: source\ndata: {json.dumps(retrieved_docs)}\n\n"
        logger.info("已将溯源文档事件发送到前端")

        # b. 准备并开始流式调用 vLLM
        payload = {
            "model": settings.VLLM_MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            "enable_thinking": True,
            "max_tokens": 1024,
            "stream": True 
        }

        headers = {
            "Authorization": f"Bearer sk-this-can-be-anything"
        }
        logger.info(f"正在调用 vLLM 模型服务: {settings.VLLM_API_URL}")
        try: 
            async with httpx.AsyncClient() as client:
                # 调用模型客户端接口获取流式响应
                async with client.stream("POST", settings.VLLM_API_URL, json=payload, headers=headers, timeout=60.0) as response:
                    response.raise_for_status()
                    logger.info("成功连接到 vLLM 流式服务")
                    # 流式处理部分
                    # vLLM 的 OpenAI 兼容接口返回 SSE 格式的流 (Server-Sent Events)
                    async for line in response.aiter_lines():  # aiter_lines 用于异步迭代器，运行逐行读取异步生成的数据
                        if line.startswith("data:"):  # 处理数据
                            data_str = line[len("data:"):].strip()
                            if data_str == "[DONE]":
                                break
                            if not data_str:
                                continue
                            try:
                                chunk = json.loads(data_str)
                                if 'choices' in chunk and chunk['choices'][0].get('delta', {}).get('content'):
                                    token = chunk['choices'][0]['delta']['content']
                                    # 将每个 token 作为 'token' 事件发送
                                    yield f"event: token\ndata: {json.dumps({"token": token})}\n\n" 
                            except json.JSONDecodeError:
                                continue
            logger.info("vLLM 流式传输完成")
        except Exception as e:
            logger.error(f"调用LLM流式接口时出错: {e}", exc_info=True)
            error_message = json.dumps({"error": "处理请求时发生内部错误"})
            yield f"event: error\ndata: {error_message}\n\n"
        yield "event: end\ndata: {}\n\n"
    return StreamingResponse(stream_generator(), media_type="text/event-stream")