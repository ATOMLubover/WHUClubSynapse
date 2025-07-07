import httpx
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse
from app.utils.auth import get_api_key
from app.configs.config import settings
# from app.rag.mcp_rag_service import retrieve, format_context
from app.schemas import SearchQuery, SearchResponse
from app.utils.singleton import logger

def build_final_prompt(user_query: str, context_str: str):
    return f"""你是一位顶级的AI信息分析与总结专家。你的核心任务是深入分析用户问题和系统提供的参考资料，然后输出一份逻辑清晰、信息全面、高度浓缩的优质回答。

**[用户原始问题]**
{user_query}


**[系统检索到的参考资料]**
{context_str}

**[你的输出要求]**

1.  **忠于资料**：你的回答必须**基于**上面提供的“[系统检索到的参考资料]”进行构建。

2.  **核心是“整合”与“提炼”**：不要简单地复制或罗列资料中的句子。你的价值在于**深度理解**所有信息，将关键点**提炼**出来，然后用**你自己的话**重新组织成一个逻辑连贯、易于理解的整体。

3.  **处理资料不足的情况**：如果参考资料确实无法回答用户的问题，或者问题与资料完全无关，请结合你的通用知识进行回答。

4.  **采用“金字塔”结构化输出**：为了达到最佳的可读性，请严格遵循以下“先总后分”的结构来组织你的回答，确保每一部分都服务于核心摘要：
    *   **【核心摘要】**：用一到两句高度概括的话，直接、明确地给出问题的最终答案。让用户在3秒内就能抓住核心。
    *   **【详细解读】**：在核心摘要的基础上展开，可以分点或分段进行详细阐述。使用加粗的小标题来区分不同的信息模块（例如：**背景介绍**、**关键步骤**、**不同方案对比**等），使结构一目了然。
    *   **【要点补充】**：在回答的最后，提供一些画龙点睛的补充信息，例如相关的注意事项、实用技巧或延伸知识，以提升回答的深度和实用性。

5.  **专业的语言风格**：请使用客观、中立、专业的语言。避免使用口语化的、模糊不清的词汇。你的目标是成为一个可靠的信息来源。

6.  **保持回答的独立性**：在你的回答内容中，绝对不要提及你参考了“资料”或“上下文”，让最终的输出看起来就像一篇由你独立撰写的分析报告。

请使用 Markdown 格式化你的回答，确保内容友好、易于理解。
请现在开始你的分析与总结。
"""

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

    # 1. 通过 HTTP 调用 RAG 微服务进行文档检索和格式化
    retrieved_docs = []
    context_str = ""
    try:
        # 使用同一个 httpx.AsyncClient 实例来处理两个连续的请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            # --- 第一步：检索文档 ---
            retrieve_response = await client.post(
                settings.INTERNAL_RAG_API_URL + "/retrieve",
                json={"query": user_query, "n_results": settings.RAG_N_RESULT},
            )
            retrieve_response.raise_for_status()
            
            # httpx 的 .json() 方法已经将响应体解析为 Python 字典
            # 服务器修正后，response 的值直接就是文档列表
            retrieved_docs = retrieve_response.json()["response"]
            
            if not retrieved_docs:
                logger.warning("RAG 服务未检索到任何文档。")
            
            # --- 第二步：格式化上下文 ---
            format_response = await client.post(
                settings.INTERNAL_RAG_API_URL + "/format",
                # 直接发送上一步获取的 Python 列表
                json={"retrieved_docs": retrieved_docs},
            )
            format_response.raise_for_status()
            
            # 服务器修正后，这里的 text 字段直接就是格式化好的字符串
            response_data = format_response.json()
            if response_data["response"]:
                context_str = response_data["response"][0]["text"]

    except httpx.RequestError as e:
        logger.error(f"调用RAG服务失败: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"无法连接到内部检索服务: {str(e)}")
    except Exception as e:
        logger.error(f"RAG 检索或格式化失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理检索文档时出错: {str(e)}")

    # 2. 构建增强提示
    final_prompt = build_final_prompt(user_query, context_str)
    
    logger.debug(f"构建的最终提示 (前300字符): {final_prompt[:300]}...")

    # 3. 定义一个异步生成器，用于流式处理
    async def stream_generator():
        # a. 通过 SSE 发送溯源文档事件
        # logger.debug(f"retrieved_docs: {type(retrieved_docs[0])}")
        yield f"event: source\ndata: {json.dumps(retrieved_docs, ensure_ascii=False)}\n\n"
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
            "stream": True,
            "lora_request": {
                "lora_name": settings.VLLM_LORA_NAME,
                "lora_int_id": settings.VLLM_LORA_ID,
                "lora_local_path": settings.VLLM_LORA_DIR
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.VLLM_API_KEY}"
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
            error_message = json.dumps({"error": "处理请求时发生内部错误"}, ensure_ascii=False)
            yield f"event: error\ndata: {error_message}\n\n"
        yield "event: end\ndata: {}\n\n"
    return StreamingResponse(stream_generator(), media_type="text/event-stream")