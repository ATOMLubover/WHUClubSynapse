import json
import signal
import time
import logging
from typing import List, Dict, Tuple
import chromadb
import os
from redis import Redis, exceptions
import threading
import redis
import base64
from datetime import datetime
from extract_club_data import extract_club_data

# 配置
# Redis 连接配置
REDIS_HOST: str = "8.141.92.242"
REDIS_PORT: int = 6379
REDIS_PASSWORD: str = "_pwdForRedis1"
REDIS_STREAM_NAME: str = "rag_sync_stream"
REDIS_CONSUMER_GROUP_NAME: str = "rag_sync_consumer_group0"
REDIS_CONSUMER_NAME: str = f"sync-worker-{os.uname().nodename}-{os.getpid()}"  # 动态生成消费者名称
REDIS_MESSAGES_PER_PULL: int = 64
REDIS_BLOCK_TIMEOUT_MS: int = 10000

# 本地数据存储配置
LOCAL_OUTPUT_FILE: str = "local_synced_data.jsonl"

# 日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量
SHUTDOWN_REQUESTED = False
seen_ids = set() # 用于存储已同步的文档ID

# Redis 连接池（独立版本，直接创建）
redis_pool = None # 稍后在 run_sync_worker 中初始化

def load_existing_ids(filename):
    """
    加载已同步的 dynamic 文档 ID 到内存中，用于去重。
    """
    if not os.path.exists(filename):
        return

    logger.info(f"正在加载现有文档ID进行去重: {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line)
                if 'id' in data and data['id'].startswith('dynamic::'):
                    seen_ids.add(data['id'])
            except json.JSONDecodeError as e:
                logger.warning(f"解析现有文件行时出错: {line.strip()} - {e}")
    logger.info(f"已加载 {len(seen_ids)} 个现有文档ID。")

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

def encode_binary_data(data):
    """
    将二进制数据编码为 base64 字符串
    """
    if isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')
    return data

def decode_base64(data):
    """
    解码 base64 数据。如果 data 是字节串，尝试直接UTF-8解码，失败则尝试base64解码并UTF-8解码。
    如果 data 是字符串，尝试base64解码并UTF-8解码。
    如果所有尝试都失败，则返回原始数据（如果是字符串）或特定标记字符串（如果是字节串且无法解码）。
    """
    if data is None:
        return None
    
    if isinstance(data, bytes):
        try:
            return data.decode('utf-8') # 尝试直接解码为UTF-8
        except UnicodeDecodeError:
            try:
                # 尝试base64解码后再UTF-8解码
                return base64.b64decode(data).decode('utf-8')
            except (base64.binascii.Error, UnicodeDecodeError):
                # 既不是UTF-8也不是有效的base64编码文本，返回一个带截断base64的标记
                return f"[BINARY_DATA_NOT_TEXT: {base64.b64encode(data).decode('utf-8')[:50]}...]"
    elif isinstance(data, str):
        try:
            # 尝试base64解码字符串
            return base64.b64decode(data).decode('utf-8')
        except (base64.binascii.Error, UnicodeDecodeError):
            # 如果不是有效的base64编码字符串，则返回原始字符串
            return data
    else:
        return str(data) # 将其他类型转换为字符串

def process_redis_value(value):
    """
    处理 Redis 值，将二进制数据和 base64 编码的字符串转换为正常文字。
    """
    if isinstance(value, bytes) or isinstance(value, str):
        return decode_base64(value) # 使用统一的解码函数
    elif isinstance(value, dict):
        processed_dict = {}
        for k, v in value.items():
            processed_key = process_redis_value(k) # 递归处理键
            processed_value = process_redis_value(v) # 递归处理值
            processed_dict[processed_key] = processed_value
        return processed_dict
    elif isinstance(value, (list, tuple, set)):
        return [process_redis_value(v) for v in value] # 递归处理列表/元组/集合
    else:
        return value # 返回原始值（对于 int, float, bool, None）

def connect_redis():
    """
    连接到 Redis 服务器
    """
    return redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=False  # 保持原始二进制数据
    )

def process_dynamic_data(key, data):
    """
    处理动态数据（业务数据）
    """
    try:
        # 解码 key 中的 base64 部分
        prefix, encoded_id = key.split(b'::', 1)
        prefix = prefix.decode('utf-8')
        real_id = decode_base64(encoded_id)
        if real_id is None:
            logger.warning(f"无法解码动态数据键中的 base64 ID: {encoded_id}")
            return None
        
        result = {
            'id': f"{prefix}::{real_id}",
            'document': None,
            'metadata': {}
        }
        
        # 处理文档数据
        if isinstance(data, dict):
            # 获取并解码文档内容
            if b'document' in data:
                result['document'] = decode_base64(data[b'document'])
                if result['document'] is None:
                    logger.warning(f"无法解码动态数据文档内容，跳过: {key}")
                    return None
            
            # 获取并解码元数据
            if b'metadata' in data:
                metadata = data[b'metadata']
                if isinstance(metadata, dict):
                    decoded_metadata = {}
                    for k, v in metadata.items():
                        key_str = k.decode('utf-8') if isinstance(k, bytes) else str(k)
                        value = decode_base64(v)
                        if value is None:
                            logger.warning(f"无法解码动态数据元数据值，跳过此元数据项: {key_str}")
                            continue # 跳过此元数据项，而不是整个文档
                        try:
                            # 如果是 JSON 字符串，解析它
                            if isinstance(value, str):
                                value = json.loads(value)
                        except json.JSONDecodeError:
                            pass # 不是 JSON 字符串，按原样使用
                        decoded_metadata[key_str] = value
                    result['metadata'] = decoded_metadata
        elif isinstance(data, bytes):
            # 如果数据是字节串，直接解码为文档内容
            result['document'] = decode_base64(data)
            if result['document'] is None:
                logger.warning(f"无法解码动态数据字节串为文档内容，跳过: {key}")
                return None
            
        return result
    except Exception as e:
        logger.error(f"处理动态数据时出错: {str(e)}")
        return None

def process_metric_data(key, value, data_type):
    """
    处理度量数据（性能计数器数据）
    """
    result = {
        'id': key.decode('utf-8'),
        'type': data_type,
        'key': key.decode('utf-8'),
        'timestamp': time.time()
    }
    
    if data_type == 'hash':
        processed_hash = {}
        for k, v in value.items():
            processed_hash[decode_base64(k)] = decode_base64(v)
        result['value'] = processed_hash
    elif data_type == 'set':
        result['value'] = [decode_base64(item) for item in value]
    elif data_type == 'stream':
        processed_stream = []
        for stream_id, messages in value:
            for message_id, message_data in messages:
                decoded_message_data = {}
                for mk, mv in message_data.items():
                    decoded_message_data[decode_base64(mk)] = decode_base64(mv)
                processed_stream.append({
                    'id': decode_base64(message_id),
                    'data': decoded_message_data
                })
        result['value'] = processed_stream
    else:
        result['value'] = decode_base64(value)
    
    return result

def save_to_jsonl(data, filename):
    """
    将数据保存到 JSONL 文件
    """
    if data:
        with open(filename, 'a', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            f.write('\n')

def sync_redis_data(output_file='local_synced_data.jsonl'):
    """
    同步 Redis 数据到本地文件
    """
    r = connect_redis()
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # 获取所有键
    for key in r.scan_iter("*"):
        try:
            # 只处理 dynamic:: 开头的键
            if not key.startswith(b'dynamic::'):
                continue

            # 获取键的类型
            key_type = r.type(key)
            
            # 处理业务数据
            if key_type == b'hash':
                value = r.hgetall(key)
                data = process_dynamic_data(key, value)
            else:
                value = r.get(key)
                data = process_dynamic_data(key, {'document': value})
            
            if data is None:
                logger.warning(f"跳过无法处理的动态数据键: {key.decode('utf-8', errors='replace')}")
                continue

            # 检查 ID 是否已存在，如果存在则跳过
            if data['id'] in seen_ids:
                logger.debug(f"跳过重复的 dynamic ID: {data['id']}")
                continue
            
            # 保存到文件
            save_to_jsonl(data, output_file)
            seen_ids.add(data['id']) # 将新的 ID 添加到已同步集合

        except Exception as e:
            logger.error(f"处理键 {key} 时出错: {str(e)}")
            continue

# 批量消息处理
def process_messages_batch(messages: List[Tuple[str, Dict[str, str]]]):
    """
    一次性处理一批消息，将大文档直接存储。
    """
    first_msg_id = messages[0][0].decode('utf-8', errors='replace') if isinstance(messages[0][0], bytes) else messages[0][0]
    last_msg_id = messages[-1][0].decode('utf-8', errors='replace') if isinstance(messages[-1][0], bytes) else messages[-1][0]
    logger.debug(f"Parsing batch of {len(messages)} messages from {first_msg_id} to {last_msg_id}.")

    batch_ids, batch_metadatas, batch_documents = [], [], []
    processed_msg_ids = []

    for msg_id, msg_data in messages:
        try:
            # 解码消息 ID
            msg_id = msg_id.decode('utf-8', errors='replace') if isinstance(msg_id, bytes) else msg_id
            
            # 处理消息数据
            if isinstance(msg_data, bytes):
                msg_data = process_redis_value(msg_data)
            elif isinstance(msg_data, dict):
                msg_data = {
                    k.decode('utf-8', errors='replace') if isinstance(k, bytes) else k: 
                    process_redis_value(v) for k, v in msg_data.items()
                }

            # 直接以字符串形式获取 source_id 和 content
            source_id_base = msg_data.get('source_id')
            if isinstance(source_id_base, dict) and source_id_base.get('_type') == 'binary':
                source_id_base = source_id_base.get('data', '')
            content = msg_data.get('content')
            if isinstance(content, dict) and content.get('_type') == 'binary':
                content = content.get('data', '')

            # 检查必要字段是否存在且不为空
            if not source_id_base or not content:
                raise ValueError("Message is missing 'source_id' or 'content', or they are empty.")

            source_id = "dynamic::" + str(source_id_base)
            
            # 跳过来自Stream的测试键 (pcp:)
            if source_id.startswith("dynamic::pcp:"):
                logger.debug(f"跳过来自Stream的测试键: {source_id}")
                processed_msg_ids.append(msg_id) # 即使跳过，也要确认消息，防止毒丸消息
                continue # 跳过处理和保存此消息

            # 检查 ID 是否已存在，如果存在则跳过
            if source_id in seen_ids:
                logger.debug(f"跳过重复的 dynamic::Stream ID: {source_id}")
                processed_msg_ids.append(msg_id) # 即使跳过，也要确认消息
                continue # 跳过处理和保存此消息

            # 安全地处理 metadata
            metadata_str = msg_data.get('metadata', '')
            try:
                if isinstance(metadata_str, bytes):
                    metadata_str = metadata_str.decode('utf-8', errors='replace')
                elif isinstance(metadata_str, dict):
                    if metadata_str.get('_type') == 'binary':
                        metadata_str = metadata_str.get('data', '')
                    else:
                        # 如果是普通字典，直接使用
                        raw_metadata = metadata_str
                        metadata_str = None  # 标记已经处理为字典

                if metadata_str is not None:  # 如果还没有处理为字典
                    if metadata_str.strip():
                        try:
                            raw_metadata = json.loads(metadata_str)
                        except json.JSONDecodeError:
                            # 如果不是有效的JSON，将其作为纯文本处理
                            raw_metadata = {"text": metadata_str}
                    else:
                        raw_metadata = {}

                sanitized_metadata = {
                    str(key): sanitize_metadata_value(value) 
                    for key, value in raw_metadata.items()
                }

                if not sanitized_metadata:
                    sanitized_metadata['source'] = str(source_id_base)

                # 为每个切分出的文本块准备数据
                batch_ids.append(source_id)
                batch_documents.append(content)
                batch_metadatas.append(sanitized_metadata)

                processed_msg_ids.append(msg_id)

            except Exception as e:
                logger.error(f"处理 metadata 时出错: {str(e)}", extra={"msg_id": msg_id})
                # 使用默认的 metadata
                sanitized_metadata = {'source': str(source_id_base)}
                batch_ids.append(source_id)
                batch_documents.append(content)
                batch_metadatas.append(sanitized_metadata)
                processed_msg_ids.append(msg_id)

        except Exception as e:
            logger.error(f"Failed to parse or process message. Error: {str(e)}", extra={"msg_id": msg_id})

    if not batch_documents:
        # 如果所有消息都解析失败，也要返回ID以便ACK，防止毒丸消息
        return [msg_id.decode('utf-8', errors='replace') if isinstance(msg_id, bytes) else msg_id 
                for msg_id, _ in messages] if messages else []

    try:
        # 将数据写入本地文件
        with open(LOCAL_OUTPUT_FILE, 'a', encoding='utf-8') as f:
            for i in range(len(batch_ids)):
                data_to_save = {
                    "id": batch_ids[i],
                    "document": batch_documents[i],
                    "metadata": batch_metadatas[i]
                }
                f.write(json.dumps(data_to_save, ensure_ascii=False) + '\n')
                seen_ids.add(batch_ids[i]) # 将新的 ID 添加到已同步集合

        logger.info(
            f"成功处理 {len(batch_ids)} 个文档，并将数据写入本地文件：{LOCAL_OUTPUT_FILE}")
        return processed_msg_ids

    except Exception as e:
        logger.error(f"写入本地文件失败: {str(e)}", extra={"msg_id": "batch_operation"})
        return []  # 批量处理失败，不ACK，以便重试

# 主运行循环
def run_sync_worker():
    global redis_pool # 引用全局变量

    # 初始化 Redis 连接池
    if redis_pool is None:
        redis_pool = Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=False # 禁用自动解码功能
        )

    r = redis_pool # 从连接池获取连接

    # 加载已存在的 ID
    load_existing_ids(LOCAL_OUTPUT_FILE)

    # 确保 Stream 和消费者组存在
    try:
        r.xgroup_create(
            name=REDIS_STREAM_NAME,
            groupname=REDIS_CONSUMER_GROUP_NAME,
            id='0',  # 从头开始读取
            mkstream=True
        )
    except exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
        else:
            # 如果消费者组已存在，重置其位置到流的开始
            try:
                r.xgroup_destroy(REDIS_STREAM_NAME, REDIS_CONSUMER_GROUP_NAME)
                r.xgroup_create(
                    name=REDIS_STREAM_NAME,
                    groupname=REDIS_CONSUMER_GROUP_NAME,
                    id='0',  # 从头开始读取
                    mkstream=True
                )
            except Exception as e:
                logger.error(f"重置消费者组失败: {e}")
                raise

    while not SHUTDOWN_REQUESTED:
        logger.info("开始同步数据库...")
        try:
            # 从 Stream 拉取消息
            messages = r.xreadgroup(
                groupname=REDIS_CONSUMER_GROUP_NAME,
                consumername=REDIS_CONSUMER_NAME,
                streams={REDIS_STREAM_NAME: '>'},
                count=REDIS_MESSAGES_PER_PULL,
                block=REDIS_BLOCK_TIMEOUT_MS
            )
            
            if not messages:
                continue

            # messages[0][0] 是 stream name, messages[0][1] 是消息列表
            message_list = messages[0][1]

            # 调用批量处理函数
            successfully_processed_ids = process_messages_batch(message_list)

            # 确认消息处理完成
            if successfully_processed_ids:
                r.xack(REDIS_STREAM_NAME, REDIS_CONSUMER_GROUP_NAME, *successfully_processed_ids)
            extract_club_data()
            print(f"社团数据已提取并保存")

        except exceptions.ConnectionError as e:
            logger.error(f"Redis 连接错误: {e}. 5秒后重试...", extra={'msg_id': 'N/A'})
            time.sleep(5)
        except Exception as e:
            logger.error(f"主循环中发生未知错误: {e}", extra={'msg_id': 'N/A'})
            time.sleep(5)

def main():
    """
    主函数
    """
    output_file = 'local_synced_data.jsonl'
    print(f"开始同步数据到 {output_file}")
    sync_redis_data(output_file)
    print("同步完成")

if __name__ == "__main__":
    # 注册信号处理器
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    run_sync_worker()
    main()