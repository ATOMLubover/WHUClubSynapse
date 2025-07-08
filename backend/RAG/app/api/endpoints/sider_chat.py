import httpx
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse
from typing import List, Dict, Any
from app.utils.auth import get_api_key
from app.schemas import ChatMessage, ChatQuery, ChatResponse
from app.configs.config import settings
# from app.rag.mcp_rag_service import retrieve, format_context
from app.utils.singleton import logger

router = APIRouter(
    dependencies=[Depends(get_api_key)]
)

@router.get("/sider-chat", summary="侧边栏对话接口测试")
def test_sider_chat():
    return "sider-chat 接口的 GET 请求成功了！"

# --- Helper Functions (Pure or Near-Pure Logic) ---
def _format_history(history: List[ChatMessage]) -> str:
    """
    Formats the chat history list into a readable string. Pure function
    """
    if not history:
        return "无历史对话"
    return "\n".join([f"{msg.role}: {msg.content}" for msg in history])


def build_final_prompt(user_query: str, history_str: str, context_str: str) -> str:
    """
    构造一个更适合对话聊天场景的、发送给语言模型的最终 prompt。
    """
    # 这个模板将AI设定为一个友好、专业的助手角色
    return f"""你好！你是一个友好、专业的“社团管理系统”AI助手。你的目标是与用户进行自然流畅的对话，为他们提供清晰、有帮助的回答。

现在，请你基于我们之前的对话，并参考我为你找到的背景资料，以及必要时运用你自己的知识，来回答用户的最新问题。


**对话历史 (供参考):**
{history_str}


**相关背景资料 (参考):**
{context_str}


**用户的最新问题:**
{user_query}


**回复时请注意：**

1.  **像一个真正的助手一样**：请用友好、热情的语气进行回复，让用户感觉在与一个乐于助人的人类专家交谈。
2.  **聚焦核心问题**：始终聚焦于用户的“最新问题”。请用你自己的话来组织和解释信息，而不是直接复述背景资料。
3.  **灵活运用资料**：请优先使用“相关背景资料”。如果资料不足以回答，或者问题与社团管理无关，再自然地切换到你的通用知识来提供帮助。
4.  **保持神秘感**：请不要在回答中提及你参考了“背景资料”或任何内部文档，让回答看起来像是源于你自己的知识。
5.  **保持清晰结构**：如果内容比较复杂，可以使用结构化的方式来组织回答，使其易于理解。

请使用 Markdown 格式化你的回答，确保内容友好、易于理解。
请开始你的回复吧！
"""


@router.post("/sider-chat", summary="RAG侧边栏对话接口")
async def sider_chat(chat_query: ChatQuery, enable_thinking: bool = True):
    """
    Receives user query and history, enhances with RAG, and returns a response.
    This function orchestrates the calls to helper functions.
    """
    user_query = chat_query.query
    if not user_query:
        raise HTTPException(status_code=400, detail="没有收到查询内容")

    logger.info(f"收到新的聊天请求, 最新查询: '{user_query}'")
    logger.info(f"本次请求包含 {len(chat_query.history)} 条历史记录")

    try:
        # 1. 通过 HTTP 调用 RAG 微服务进行文档检索和格式化
        async with httpx.AsyncClient(timeout=30.0) as client:
            # --- 第一步：检索文档 ---
            retrieve_response = await client.post(
                settings.INTERNAL_RAG_API_URL + "/retrieve",
                json={"query": user_query, "n_results": settings.RAG_N_RESULT},
            )
            retrieve_response.raise_for_status()
            retrieved_docs = retrieve_response.json()["response"]
            
            if not retrieved_docs:
                logger.warning("RAG 服务未检索到任何文档。")

            # --- 第二步：格式化上下文 ---
            format_response = await client.post(
                settings.INTERNAL_RAG_API_URL + "/format",
                json={"retrieved_docs": retrieved_docs},
            )
            format_response.raise_for_status()
            response_data = format_response.json()
            if response_data.get("response"):
                context_str = response_data["response"][0]["text"]

        # 2. 格式化历史记录
        history_str = _format_history(chat_query.history)

        # 3. 构建最终提示
        final_prompt = build_final_prompt(user_query, history_str, context_str)
        logger.debug(f"构建的最终提示 (前100字符): {final_prompt[:100]}...")

        history_messages = [msg.model_dump() for msg in chat_query.history]
        messages_for_llm = history_messages + [{"role": "user", "content": final_prompt}]

    except httpx.RequestError as e:
        logger.error(f"调用RAG服务失败: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"无法连接到内部检索服务: {str(e)}")
    except Exception as e:
        logger.error(f"RAG 检索或格式化失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"检索相关文档时出错: {str(e)}")

    async def stream_generator():
        # a. 通过 SSE 发送溯源文档事件
        # 修正：发送 retrieved_docs 列表，而不是一个字符串
        source_event = f"event: source\ndata: {json.dumps(retrieved_docs, ensure_ascii=False)}\n\n"
        logger.info(f"向前端发送溯源事件，共 {len(retrieved_docs)} 个文档")
        logger.debug(f"发送 SSE 事件: {source_event.strip()}")
        logger.info("已将溯源文档事件发送到前端")
        yield source_event

        payload = {
            "model": settings.VLLM_MODEL_NAME,
            "messages": messages_for_llm,
            "max_tokens": 1024,
            "stream": True,
            "enable_thinking": enable_thinking,
            "lora_request": {
                "lora_name": settings.VLLM_LORA_NAME,
                "lora_int_id": settings.VLLM_LORA_ID,
                "lora_local_path": settings.VLLM_LORA_DIR
            }
        }
        headers = {"Authorization": "Bearer sk-this-can-be-anything"}

        logger.info(f"正在调用 vLLM 模型服务: {settings.VLLM_API_URL}")
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream("POST", settings.VLLM_API_URL, json=payload, headers=headers, timeout=60.0) as response:
                    response.raise_for_status()
                    logger.info("成功连接到 vLLM 流式服务")
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            data_str = line[len("data: "):].strip()
                            if data_str == "[DONE]":
                                break
                            if not data_str:
                                continue
                            try:
                                chunk = json.loads(data_str)
                                if 'choices' in chunk and chunk['choices'][0].get('delta', {}).get('content'):
                                    token = chunk['choices'][0]['delta']['content']
                                    token_event = f"event: token\ndata: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
                                    logger.debug(f"发送 SSE token: {token.strip()}")
                                    yield token_event
                            except json.JSONDecodeError:
                                continue
            logger.info("vLLM 流式传输完成")
        except Exception as e:
            logger.error(f"调用LLM流式接口时出错: {e}", exc_info=True)
            error_message = json.dumps({"error": "处理请求时发生内部错误"})
            error_event = f"event: error\ndata: {error_message}\n\n"
            logger.error(f"向前端发送错误事件: {error_event.strip()}")
            yield error_event
        
        end_event = "event: end\ndata: {}\n\n"
        logger.info(f"向前端发送结束事件: {end_event.strip()}")
        yield end_event

    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Connection": "keep-alive",
        "Pragma": "no-cache", # 兼容旧版
        "Expires": "0",
        "X-Accel-Buffering": "no" # 尝试性地给 Nginx 类代理发送信号
    }

    return StreamingResponse(stream_generator(), media_type="text/event-stream", headers=headers)
