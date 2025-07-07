import httpx
import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse
from typing import List, Dict, Any
from app.utils.auth import get_api_key
from app.schemas import ChatMessage, ChatQuery, ChatResponse
from app.configs.config import settings
from app.utils.singleton import logger

router = APIRouter(
    dependencies=[Depends(get_api_key)]
)

@router.get("/health", summary="健康状态接口")
def health():
    """
    健康检查接口
    """
    return {"status": "healthy", "service": "fastapi-backend"}