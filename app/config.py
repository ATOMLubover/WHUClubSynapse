from pydantic_settings import  BaseSettings
import os

class Settings(BaseSettings):
    # vLLM OpenAI格式兼容 API 端口
    VLLM_API_BASE: str = "http://localhost:8000/v1"
    VLLM_API_KEY: str = "sk-xxx"  # 离线部署随便写一个，只是需要它来通过 api key 的验证
    MODEL_NAME: str = "Qwen3-8B"
    MODEL_DIR: str = "/root/autodl-tmp/Qwen/Qwen3-8B"

    # 嵌入模型配置
    EMBEDDING_MODEL_NAME: str = "moka-ai/m3e-base"
    EMBEDDING_MODEL_DIR: str = "/root/autodl-tmp/AI-ModelScope/all-MiniLM-L6-v2"

    # 向量数据库配置
    CHROMA_SERVER_HOST: str = "127.0.0.1"
    CHROMA_SERVER_PORT: int = 8040
    CHROMA_SERVER_SSL: bool = False  # 是否启用 HTTPS
    CHROMA_RAG_COLLECTION_NAME: str = "club_management_rag"
    STATIC_DOC_PATH: str = "/root/autodl-tmp/static_doc"

    # Redis 连接配置
    REDIS_HOST: str = "8.141.92.242"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: str = "admin"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = "_pwdForRedis1"
    REDIS_STREAM_NAME: str = "rag_sync_stream"
    REDIS_CONSUMER_GROUP_NAME: str = "rag_sync_consumer_group0"
    REDIS_CONSUMER_NAME: str = f"sync-worker-{os.uname().nodename}-{os.getpid()}"  # 动态生成消费者名称
    REDIS_MESSAGES_PER_PULL: int = 10
    REDIS_BLOCK_TIMEOUT_MS: int = 10000

    # 日志配置
    LOG_LEVEL: str = "ERROR"

# 读取配置
settings = Settings()