from redis import ConnectionPool, Redis
from app.config import settings
import logging
import json
import time
import signal
from app.rag_service import get_embeddings

# 日志记录设置
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - [MessageID: %(msg_id)s] - %(message)s'
)

log = logging.getLogger(__name__)

# redia连接池，只在脚本启动时创建一次
redis_pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)

class VectorDBClient:
    def upsert(self, vector_id: str, vector: list, metadata: dict):
        pass

vector_db = VectorDBClient()

# 消息处理
def process_message(msg_id, msg_data):
    try:
        data = json.loads(msg_data['data'])
        source_id = data.get('source_id')
        content = data.get('content')

        if not all([source_id, content]):
            raise ValueError("Message is missing 'source_id' or 'content'")

        # 向量化
        vector = get_embeddings(content)
        # 写入向量数据库
        vector_db.upsert(vector_id=source_id, vector=vector, metadata=data.get('metadata', {}))

        return True
    except Exception as e:
        log.error(f"Failed to process message. Error: {e}", extra={"msg_id": msg_id})
        return False

# 主运行循环
def run_sync_worker():
    r = redis.Redis(ConnectionPool=redis_pool)
    # 确保 Strean 和消费者组存在
    try:
        r.xgroup_create(
            name=settings.REDIS_STREAM_NAME,
            group_name=settings.REDIS_CONSUMER_GROUP_NAME,
            id='0-0',
            mkstream=True
        )
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
    while True:
        try:
            # 从 Stream 拉取一批新消息
            messages = r.xreadgroup(
                groupname=settings.REDIS_CONSUMER_GROUP_NAME,
                consumername=settings.REDIS_CONSUMER_NAME,
                streams={settings.REDIS_STREAM_NAME: '>'},
                count=settings.REDIS_MESSAGES_PER_PULL,
                block=settings.REDIS_BLOCK_TIMEOUT_MS
            )
            if not messages:
                continue
            # 处理拉取到的消息
            for stream, msgs in messages:
                for msg_id, msg_data in msgs:
                    process_message(msg_id, msg_data)
                    # 无论成功与否都 ACK，防止格式错误/处理失败的“毒丸消息”反复投递，阻塞队列
                    r.xack(settings.REDIS_STREAM_NAME, settings.REDIS_CONSUMER_GROUP_NAME, msg_id)
        except redis.exceptions.ConnectionError as e:
            # 对于连接错误，打印日志并等待一段时间后重试
            log.error(f"Redis connection error: {e}. Retrying in 5 seconds...", extra={'msg_id': 'N/A'})
            time.sleep(5)
        except Exception as e:
            # 对于其他未知循环错误，同样记录并重试
            log.error(f"An unexpected error occurred in the main loop: {e}", extra={'msg_id': 'N/A'})
            time.sleep(5)

if __name__ == "__main__":
    run_sync_worker()