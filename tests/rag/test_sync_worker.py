import json
import logging
import random
import time
import redis
from app.config import settings
from app.utils.singleton import redis_pool

# --- 日志设置 ---
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - [PRODUCER] - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

# 模拟的消息模板, 我们将从这里随机选择来模拟不同来源的数据
MOCK_MESSAGES_TEMPLATES = [
    {
        "content": "社团招新啦！技术部需要Python和Go开发人员，快来加入我们，一起构建超酷的项目！",
        "metadata": {
            "source_type": "announcement",
            "department": "tech_dept",
            "tags": ["recruitment", "python", "go"]
        }
    },
    {
        "content": "本周五晚7点，将在活动室301举办AI大模型技术分享会，主讲人张三将分享最新的大模型微调技术。",
        "metadata": {
            "source_type": "event",
            "title": "AI大模型技术分享会",
            "author": "张三",
            "tags": ["ai", "llm", "workshop"]
        }
    },
    {
        "content": "大家好，我是新加入宣传部的李四。我非常擅长视频剪辑和海报设计，希望能为社团贡献自己的一份力量。",
        "metadata": {
            "source_type": "member_update",
            "member_name": "李四",
            "department": "publicity_dept"
        }
    },
    {
        "content": "财务部提醒：请所有项目组在本月底前提交第三季度预算申请。",
        "metadata": {
            "source_type": "reminder",
            "department": "finance_dept"
        }
    }
]


def send_mock_message(r: redis.Redis):
    """
    随机选择一个模板，构造并发送一条消息到Redis Stream。
    """
    try:
        # 1. 随机选择一个消息模板
        message_to_send = random.choice(MOCK_MESSAGES_TEMPLATES)

        # 2. 模拟一个来自数据库的source_id (这里我们用随机数代替)
        # 在真实场景中，这将是数据库的自增ID或UUID
        source_id = f"mock_id_{random.randint(1000, 9999)}"

        # 3. 构造完整的消息体
        full_message_body = {
            "source_id": source_id,
            "content": message_to_send["content"],
            "metadata": message_to_send["metadata"]
        }

        # 4. 将消息体序列化为JSON字符串
        message_payload = json.dumps(full_message_body)

        # 5. 使用 XADD 命令将消息推送到Stream
        message_id = r.xadd(
            name=settings.REDIS_STREAM_NAME,
            fields={'data': message_payload}
        )

        log.info(f"Successfully sent message to stream '{settings.REDIS_STREAM_NAME}'. Message ID: {message_id}")
        log.info(f"  > Content: \"{message_to_send['content'][:50]}...\"")

    except Exception as error:
        log.error(f"Failed to send message to Redis. Error: {error}")


if __name__ == "__main__":
    log.info("Mock producer started. Press Ctrl+C to exit.")

    # 从共享的连接池获取一个Redis连接
    redis_client = redis.Redis(connection_pool=redis_pool)

    try:
        while True:
            send_mock_message(redis_client)

            # 随机等待2到5秒，模拟真实世界的数据产生间隔
            sleep_time = random.uniform(2, 5)
            log.info(f"Waiting for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        log.warning("Producer shutting down gracefully.")
    except Exception as e:
        log.critical(f"An unexpected error occurred in the producer's main loop: {e}")