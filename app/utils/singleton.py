import logging
import chromadb
from redis import ConnectionPool

from app.configs.config import settings

logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- ChromaDB Client Singleton ---
logger.info(f"Initializing ChromaDB client to connect to {settings.CHROMA_SERVER_HOST}:{settings.CHROMA_SERVER_PORT}")

try:
    # 这个对象在模块第一次被导入时创建，之后会被所有导入者复用
    chroma_client = chromadb.HttpClient(
        host=settings.CHROMA_SERVER_HOST,
        port=settings.CHROMA_SERVER_PORT
    )

    # 我们可以把 collection 的获取也放在这里，因为它也是共享的
    chroma_collection = chroma_client.get_or_create_collection(
        name=settings.CHROMA_RAG_COLLECTION_NAME
    )
    logger.info(f"Successfully connected to ChromaDB and got collection '{settings.CHROMA_RAG_COLLECTION_NAME}'")

except Exception as e:
    logger.critical(f"Failed to initialize ChromaDB client. Exiting. Error: {e}", exc_info=True)
    # 在实际应用中，如果核心服务无法连接，直接退出
    raise

# --- Redis Client Singleton (同理，也可以把Redis连接池放在这里) ---
logger.info(f"Initializing Redis connection pool for host {settings.REDIS_HOST}")
try:
    redis_pool = ConnectionPool(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        password=settings.REDIS_PASSWORD,
        decode_responses=True
    )
except Exception as e:
    logger.critical(f"Failed to initialize Redis connection pool. Exiting. Error: {e}", exc_info=True)
    raise
