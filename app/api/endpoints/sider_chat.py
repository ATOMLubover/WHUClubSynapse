import httpx
import re
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.auth import get_api_key
from app.schemas import ChatMessage, ChatQuery, ChatResponse
from app.configs.config import settings
from app.rag.rag_service import retrieve, format_context
from app.utils.singleton import logger

router = APIRouter(
    dependencies=[Depends(get_api_key)]
)

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
    Constructs the final prompt string to be sent to the language model. Pure function.
    """
    return f"""你是一个“社团管理系统”的AI助手。你的核心任务是为用户提供清晰、准确、有用的信息。请根据下面的对话历史和为最新问题提供的参考资料来回答。

---
**对话历史:**
{history_str}
---
**为最新问题检索到的参考上下文:**
{context_str}
---
**最新用户提问:**
{user_query}
---
**你的任务指示:**

1.  **理解对话**：请仔细阅读“对话历史”以理解用户之前的提问和你的回答。
2.  **聚焦新问题**：你的主要任务是回答“最新用户提问”。
3.  **优先使用新上下文**：请优先使用“为最新问题检索到的参考上下文”来回答最新的问题。
4.  **切换通用知识**：如果新上下文不足以回答最新问题，或者问题与社团管理无关，请利用你的通用知识。
5.  **保持结构化输出**：请继续遵循以下结构来组织你的回答：
    *   **核心摘要**
    *   **关键信息/步骤**
    *   **实用技巧/补充**
6.  **回答中不要给出具体参考哪个文档**。
7.  **保持可读性**：保持总结对人类用户的可读性，避免过度分点和缩句。

请使用 Markdown 格式化你的回答，确保内容友好、易于理解。
"""


async def query_llm(prompt: str) -> str:
    """
    Sends the prompt to the vLLM service and returns the raw response content.
    This function handles the HTTP request logic.
    """
    payload = {
        "model": settings.VLLM_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 512,
        "enable_thinking": False,
        "stream": False
    }
    headers = {"Authorization": f"Bearer sk-this-can-be-anything"}

    logger.info(f"正在调用 vLLM 模型服务: {settings.VLLM_API_URL}")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.VLLM_API_URL,
            json=payload,
            headers=headers,
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']


def clean_llm_answer(answer: str) -> str:
    """
    Post-processes the raw answer from the LLM (e.g., removing <think> tags). Pure function.
    """
    return re.sub(r'<think>.*?</think>\s*', '', answer, flags=re.DOTALL).strip()


@router.post("/sider-chat", response_model=ChatResponse, summary="RAG侧边栏对话接口")
async def sider_chat(chat_query: ChatQuery):
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
        # 1. Retrieve relevant documents (I/O)
        retrieved_docs = retrieve(query=user_query, n_results=settings.RAG_N_RESULT)
        logger.info(f"为最新问题检索到 {len(retrieved_docs)} 篇相关文档")

        # 2. Format inputs (Pure computation)
        context_str = format_context(retrieved_docs=retrieved_docs)
        history_str = _format_history(chat_query.history)

        # 3. Build the prompt (Pure computation)
        final_prompt = build_final_prompt(user_query, history_str, context_str)
        logger.debug(f"构建的最终提示 (前100字符): {final_prompt[:100]}...")

        # 4. Query the Language Model (I/O)
        raw_answer = await query_llm(final_prompt)
        logger.info("成功从 vLLM 服务获取到回答")

        # 5. Clean the response (Pure computation)
        cleaned_answer = clean_llm_answer(raw_answer)

        # 6. Return the final response
        return ChatResponse(
            answer=cleaned_answer,
            source=retrieved_docs
        )

    except httpx.RequestError as e:
        logger.error(f"无法连接到离线推理服务: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"无法连接到离线推理服务: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"离线推理服务返回的数据格式无效: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"离线推理服务返回的数据格式无效: {e}")
    except Exception as e:
        logger.error(f"处理聊天请求时发生内部错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理请求时发生内部错误: {str(e)}")
