import httpx
import re
from fastapi import APIRouter, Depends, HTTPException
from app.utils.auth import get_api_key
from app.configs.config import settings
from app.rag.rag_service import retrieve, format_context
from app.schemas import SearchQuery, SearchResponse
from app.utils.singleton import logger

# 创建 FastAPI 路由，通过 dependencies 参数应用认证
router = APIRouter(
    dependencies=[Depends(get_api_key)]
)


@router.post("/smart-search", response_model=SearchResponse, summary="AI智能搜素总结接口")
async def smart_search(search_query: SearchQuery):
    """
    接收用户查询，通过 RAG 增强后调用大模型，返回最终总结及溯源信息。
    """
    user_query = search_query.query
    if not user_query:
        raise HTTPException(status_code=400, detail="没有收到查询内容")
    logger.info(f"收到新的智能搜索请求, 查询: '{user_query}'")
    try:
        # 1. 调用 RAG 服务，进行文档检索
        retrieved_docs = retrieve(query=user_query, n_results=settings.RAG_N_RESULT)
        logger.info(f"检索到 {len(retrieved_docs)} 篇相关文档")

        # 2. 格式化检索到的上下文
        context_str = format_context(retrieved_docs=retrieved_docs)

        # 3. 构建增强提示
        # 在 search.py 中构建 final_prompt 的部分
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
        logger.debug(f"构建的最终提示 (前30字符): {final_prompt[:30]}...")

        # 4. 调用 vLLM 模型服务，获取最终总结
        # a. 准备请求体和头
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
            "stream": False  # 流式响应无法返回溯源结果，而且需要分块处理
        }

        headers = {
            "Authorization": f"Bearer sk-this-can-be-anything"
        }
        logger.info(f"正在调用 vLLM 模型服务: {settings.VLLM_API_URL}")
        # b. 异步调用模型接口获取回答
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.VLLM_API_URL,
                json=payload,
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            answer = data['choices'][0]['message']['content']
        logger.info("成功从 vLLM 服务获取到回答")
        # c. 构造并返回响应
        # 清除思考输出
        clear_answer = re.sub(r'<think>.*?</think>\s*', '', answer, flags=re.DOTALL).strip()

        return SearchResponse(
            answer=clear_answer,
            source=retrieved_docs
        )
    except httpx.RequestError as e:
        logger.error(f"无法连接到离线推理服务: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"无法连接到离线推理服务: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"离线推理服务返回的数据格式无效: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"离线推理服务返回的数据格式无效: {e}")
    except Exception as e:
        logger.error(f"处理请求时发生内部错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理请求时发生内部错误: {str(e)}")
