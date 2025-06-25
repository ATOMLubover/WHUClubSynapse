import os
import uvicorn
import httpx
import fastapi
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import logging

# 加载环境变量 (例如 OPENAI_API_KEY, VLLM_BASE_URL)
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# 从环境变量获取 vLLM 服务器的 URL 和 API Key
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://127.0.0.1：8080/v1")  # vLLM 默认运行在 8000 端口
