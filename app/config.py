from pydantic_settings import  BaseSettings

class Settings(BaseSettings):
    # vLLM OpenAI-Compatible API 端口
    VLLM_API_BASE: str = "http://localhost:8000/v1"
    VLLM_API_KEY: str = "sk-xxx"  # 离线部署随便写一个，只是需要它来通过 api key 的验证
    MODEL_NAME: str = "Qwen3-8B"
    MODEL_DIR: str = "/root/autodl-tmp/Qwen/Qwen3-8B"

    # 嵌入模型配置
    EMBEDDING_MODEL_NAME: str = "moka-ai/m3e-base"
    EMBEDDING_MODEL_DIR: str = "/root/autodl-tmp/AI-ModelScope/m3e-base"

    # 向量数据库配置
    VECTOR_DB_PATH: str = "/root/autodl-tmp/chroma_db"
    VECTRO_DB_COLLECTION: str = "club_management_rag"

# 读取配置
settings = Settgings()