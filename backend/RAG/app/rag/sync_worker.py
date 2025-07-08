import json
import signal
import time
from typing import List, Dict, Tuple

from redis import Redis, exceptions

from app.configs.config import settings
from app.utils.singleton import chroma_collection, redis_pool, logger  # 从工具文件中引入向量数据库集合 和 redis连接池
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.rag.mcp_rag_service import retriever

SHUTDOWN_REQUESTED = False

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    separators=["\n\n", "\n", "。", "，", "、", " "]
)

def handle_shutdown(signum, frame):
    """停机信号处理器"""
    global SHUTDOWN_REQUESTED
    if not SHUTDOWN_REQUESTED:
        logger.warning("Shutdown signal received. Finishing current batch before exiting...")
        SHUTDOWN_REQUESTED = True


def sanitize_metadata_value(value):
    """
    【工具函数】
    如果值是列表或字典，将其JSON序列化为字符串。
    否则，按原样返回。
    """
    if isinstance(value, (list, dict)):
        try:
            # 使用紧凑的格式，不带不必要的空格
            return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
        except TypeError:
            # 如果JSON序列化失败，将其转换为字符串作为最后的保障
            return str(value)
    return value


# 批量消息处理
def process_messages_batch(messages: List[Tuple[str, Dict[str, str]]]):
    """
    一次性处理一批消息，对大文档进行切分，然后统一处理。
    """
    first_msg_id = messages[0][0]
    last_msg_id = messages[-1][0]
    logger.debug(f"Parsing batch of {len(messages)} messages from {first_msg_id} to {last_msg_id}.")

    batch_ids, batch_embeddings, batch_metadatas, batch_documents = [], [], [], []
    processed_msg_ids = []

    for msg_id, msg_data in messages:
        try:
            # 直接以字符串形式获取 source_id 和 content，使用 .get() 保证安全
            source_id_base = msg_data.get('source_id')
            content = msg_data.get('content')

            # 2. 检查必要字段是否存在且不为空
            if not source_id_base or not content:
                raise ValueError("Message is missing 'source_id' or 'content', or they are empty.")

            source_id = "dynamic::" + source_id_base

            chunks = text_splitter.split_text(content)
            logger.debug(f"Document {source_id_base} was split into {len(chunks)} chunks.")

            # 安全地处理 metadata
            metadata_str = msg_data.get('metadata', '')
            raw_metadata = json.loads(metadata_str) if metadata_str.strip() else {}
            sanitized_metadata = {key: sanitize_metadata_value(value) for key, value in raw_metadata.items()}

            if not sanitized_metadata:
                sanitized_metadata['source'] = source_id_base

            # 为每个切分出的文本块准备数据
            for i, chunk_content in enumerate(chunks):
                chunk_id = f"{source_id}::chunk::{i}"
                batch_ids.append(chunk_id)
                batch_documents.append(chunk_content)
                batch_metadatas.append(sanitized_metadata)

            processed_msg_ids.append(msg_id)

        except Exception as e:
            logger.error(f"Failed to parse or process message. Error: {e}", extra={"msg_id": msg_id})

    if not batch_documents:
        # 如果所有消息都解析失败，也要返回ID以便ACK，防止毒丸消息
        return [msg_id for msg_id, _ in messages] if messages else []

    try:
        # 批量向量化所有切分出的文本块
        batch_embeddings = retriever.get_embeddings(batch_documents)

        # 批量写入向量数据库
        chroma_collection.upsert(
            ids=batch_ids,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            documents=batch_documents
        )
        logger.info(
            f"Successfully processed and upserted {len(batch_ids)} chunks from {len(processed_msg_ids)} original messages.")
        return processed_msg_ids

    except Exception as e:
        logger.error(f"Failed to process batch embeddings/upsert. Error: {e}", extra={"msg_id": "batch_operation"})
        return []  # 批量处理失败，不ACK，以便重试

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
            logger.error(f"Redis connection error: {e}. Retrying in 5 seconds...", extra={'msg_id': 'N/A'})
            time.sleep(5)
        except Exception as e:
            # 对于其他未知循环错误，同样记录并重试
            logger.error(f"An unexpected error occurred in the main loop: {e}", extra={'msg_id': 'N/A'})
            time.sleep(5)


if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    run_sync_worker()
