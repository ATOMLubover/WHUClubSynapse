import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # vLLM OpenAI格式兼容 API 端口
    VLLM_API_URL: str = "http://localhost:8010/v1/chat/completions"
    VLLM_API_KEY: str = os.getenv('VLLM_API_KEY')
    VLLM_MODEL_NAME: str = "Qwen3-8B-AWQ"
    VLLM_MODEL_DIR: str = "/root/autodl-tmp/Qwen/Qwen3-8B-AWQ"

    VLLM_LORA_NAME: str = "Qwen-8B-AWQ-LoRA"
    VLLM_LORA_DIR: str = "/root/autodl-tmp/Qwen/Qwen3-8B-AWQ-LoRA"
    VLLM_LORA_ID: int = 0

    # 嵌入模型配置
    EMBEDDING_MODEL_NAME: str = "moka-ai/m3e-base"
    EMBEDDING_MODEL_DIR: str = "/root/autodl-tmp/AI-ModelScope/m3e-base"
    SIMILARITY_THRESHOLD: float = 0.6  # 使用嵌入模型进行上下文压缩的相似度阈值

    # 文本切分器配置
    CHUNK_SIZE: int = 300
    CHUNK_OVERLAP: int = 50

    # 向量数据库配置
    CHROMA_SERVER_HOST: str = "127.0.0.1"
    CHROMA_SERVER_PORT: int = 8030
    CHROMA_SERVER_SSL: bool = False  # 是否启用 HTTPS
    CHROMA_RAG_COLLECTION_NAME: str = "club_management_rag"
    STATIC_DOC_PATH: str = "/root/autodl-tmp/static_doc"
    RAG_N_RESULT: int = 5  # rag 检索 top-k

    # Redis 连接配置
    REDIS_HOST: str = os.getenv('REDIS_HOST')
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = os.getenv('REDIS_PASSWORD')
    REDIS_STREAM_NAME: str = "rag_sync_stream"
    REDIS_CONSUMER_GROUP_NAME: str = "rag_sync_consumer_group0"
    REDIS_CONSUMER_NAME: str = f"sync-worker-{os.uname().nodename}-{os.getpid()}"  # 动态生成消费者名称
    REDIS_MESSAGES_PER_PULL: int = 64
    REDIS_BLOCK_TIMEOUT_MS: int = 10000

    # FastAPI port
    FASTAPI_PORT: int = 8000
    INTERNAL_RAG_PORT: int = 8020
    INTERNAL_RAG_API_URL: str = "http://127.0.0.1:8020"

    # 日志配置
    LOG_LEVEL: str = "DEBUG"

    # RAGAS
    DEEPSEEK_API_URL: str ="https://api.deepseek.com/v1"
    DEEPSEEK_API_KEY: str =os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_MODEL: str ='deepseek-chat'

# 读取配置
settings = Settings()
