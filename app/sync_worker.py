from redis import ConnectionPool, Redis, exceptions
from app.config import settings
import logging
import json
import time
import signal
import uuid
from typing import List, Dict, Tuple
import chromadb
from app.rag_service import get_embeddings
from app.utils.singleton import chroma_collection, redis_pool  # 从工具文件中引入向量数据库集合 和 redis连接池

# 日志和全局标志位
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

log = logging.getLogger(__name__)

SHUTDOWN_REQUESTED = False

def handle_shutdown(signum, frame):
    """停机信号处理器"""
    global SHUTDOWN_REQUESTED
    if not SHUTDOWN_REQUESTED:
        log.warning("Shutdown signal received. Finishing current batch before exiting...")
        SHUTDOWN_REQUESTED = True

# 批量消息处理
def process_messages_batch(messages: List[Tuple[str, Dict[str, str]]]):
    """一次性处理一批消息，以提高效率"""
    """
    【临时测试版】
    一次性处理一批消息，使用随机UUID作为ID。
    注意：此版本不支持更新或删除。
    """
    first_msg_id = messages[0][0]
    last_msg_id = messages[-1][0]
    log.debug(f"Parsing batch of {len(messages)} messages from {first_msg_id} to {last_msg_id}.")
    batch_ids, batch_embeddings, batch_metadatas, batch_documents = [], [], [], []
    processed_msg_ids = []

    for msg_id, msg_data in messages:
        try:
            data = json.loads(msg_data['data'])
            source_id = "dynamic::" + data.get('source_id')
            content = data.get('content')

            # 这里是正常实现
            # if not all([source_id, content]):
            #     raise ValueError("Message is missing 'source_id' or 'content'")
            # batch_ids.append(source_id)


            # FIX: 以下是测试内容，测试完毕请删除
            if not content: # 在这个临时版本中，我们只关心content
                raise ValueError("Message is missing 'content'")
            random_id = str(uuid.uuid4())
            batch_ids.append(random_id)


            # 以下不动
            batch_documents.append(content)
            batch_metadatas.append(data.get('metadata', {}))
            processed_msg_ids.append(msg_id)


        except Exception as e:
            log.error(f"Failed to parse message. Error: {e}", extra={"msg_id": msg_id})

    if not batch_documents:
        return []  # 如果所有消息都解析失败，直接返回

    try:
        # 批量向量化
        batch_embeddings = get_embeddings(batch_documents)

        # 批量写入向量数据库
        chroma_collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            documents=batch_documents
        )
        log.info(f"Successfully processed and upserted a batch of {len(batch_ids)} messages.")
        return processed_msg_ids

    except Exception as e:
        log.error(f"Failed to process batch. Error: {e}", extra={"msg_id": "batch_operation"})
        return []  # 批量处理失败，这批消息都算失败

# 主运行循环
def run_sync_worker():
    r = Redis(connection_pool=redis_pool)
    # 确保 Stream 和消费者组存在
    try:
        r.xgroup_create(
            name=settings.REDIS_STREAM_NAME,
            groupname=settings.REDIS_CONSUMER_GROUP_NAME,
            id='0-0',
            mkstream=True
        )
    except exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise

    while not SHUTDOWN_REQUESTED:
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
            # messages[0][0] 是 stream name, messages[0][1] 是消息列表
            message_list = messages[0][1]

            # 调用批量处理函数
            successfully_processed_ids = process_messages_batch(message_list)

            # 只ACK成功处理的消息，或全部ACK，取决于业务需求。这里选择全部ACK以防止毒丸消息
            all_ids_to_ack = [msg_id for msg_id, _ in message_list]
            if all_ids_to_ack:
                r.xack(settings.REDIS_STREAM_NAME, settings.REDIS_CONSUMER_GROUP_NAME, *all_ids_to_ack)
        except exceptions.ConnectionError as e:
            # 对于连接错误，打印日志并等待一段时间后重试
            log.error(f"Redis connection error: {e}. Retrying in 5 seconds...", extra={'msg_id': 'N/A'})
            time.sleep(5)
        except Exception as e:
            # 对于其他未知循环错误，同样记录并重试
            log.error(f"An unexpected error occurred in the main loop: {e}", extra={'msg_id': 'N/A'})
            time.sleep(5)

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    run_sync_worker()