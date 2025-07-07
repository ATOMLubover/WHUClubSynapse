import httpx
import time
import asyncio
import json
import random
import string

# ==============================================================================
# 配置区域 - 请务必替换以下占位符URL为您实际的API地址！
# ==============================================================================

NGROK_LOCAL_API_URL = "https://6a52-125-220-159-5.ngrok-free.app"  # 替换为您的Ngrok本地代理API地址
TONGYI_ONLINE_API_KEY = "sk-354859a6d3ae438fb8ab9b98194f5266" # 替换为您的通义千问API Key
TONGYI_ONLINE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1" # 通义千问官方API基础URL
# ==============================================================================

TEST_ITERATIONS = 5  # 每种情况测试次数
TIMEOUT = 60  # 请求超时时间（秒）

# --- 文本生成函数 ---
def generate_text(length_type: str):
    """生成不同长度的文本"""
    if length_type == "short":
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + '你好世界' * 5, k=50))  # 50字符
    elif length_type == "medium":
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + '你好世界' * 50, k=500)) # 500字符
    elif length_type == "long":
        return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation + '你好世界' * 200, k=2000)) # 2000字符
    else:
        raise ValueError("Invalid length_type. Must be 'short', 'medium', or 'long'.")

# --- 测试函数 ---
async def test_api_latency(base_url: str, endpoint: str, payload: dict, description: str, is_stream: bool = False, headers: dict = None):
    latencies = []
    print(f"\n--- 开始测试: {description} ({base_url}{endpoint}) ---")
    for i in range(TEST_ITERATIONS):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                start_time = time.time()
                request_headers = headers if headers else {"Content-Type": "application/json"}

                if is_stream:
                    # 对于流式响应，需要完整地迭代所有数据
                    async with client.stream("POST", f"{base_url}{endpoint}", json=payload, headers=request_headers) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_bytes():
                            # 消耗所有响应数据，不进行具体处理
                            pass
                else:
                    response = await client.post(f"{base_url}{endpoint}", json=payload, headers=request_headers)
                    response.raise_for_status() # 检查HTTP错误
                    # 可以选择打印部分响应内容以验证
                    # print(f"  响应预览: {response.text[:100]}...") 
                end_time = time.time()
                latency = (end_time - start_time) * 1000 # 转换为毫秒
                latencies.append(latency)
                print(f"  测试 {i+1}/{TEST_ITERATIONS}: {latency:.2f} ms")
        except httpx.RequestError as e:
            print(f"  测试 {i+1}/{TEST_ITERATIONS} 失败 (请求错误): {e}")
        except httpx.HTTPStatusError as e:
            print(f"  测试 {i+1}/{TEST_ITERATIONS} 失败 (HTTP错误): {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"  测试 {i+1}/{TEST_ITERATIONS} 失败 (未知错误): {e}")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"--- 平均延迟: {avg_latency:.2f} ms (基于 {len(latencies)} 次成功测试) ---")
        return avg_latency
    else:
        print("--- 没有成功测试，无法计算平均延迟 ---")
        return None

async def main():
    api_configs = {
        # "代理服务器 (联网)": {"url": ONLINE_API_URL, "is_proxy": True},
        "代理服务器 (Ngrok本地)": {"url": NGROK_LOCAL_API_URL, "is_proxy": True},
        "通义千问 (官方API)": {"url": TONGYI_ONLINE_BASE_URL, "is_proxy": False, "api_key": TONGYI_ONLINE_API_KEY}
    }
    
    text_lengths = {
        "短文本": "short",
        "中文本": "medium",
        "长文本": "long"
    }

    # 测试 /chat 接口
    print("======== 测试 /chat 接口 (通用聊天 - 代理服务器) ========")
    for config_name, config_data in api_configs.items():
        if not config_data["is_proxy"]: # /chat 接口只测试代理服务器
            continue
        if config_data["url"] == "http://your_online_api_url_here" or config_data["url"] == "http://your_ngrok_local_api_url_here":
            print(f"跳过 {config_name}，因为URL未配置。请在脚本中配置相关URL。")
            continue

        for length_name, length_type in text_lengths.items():
            text = generate_text(length_type)
            payload = {
                "messages": [{"role": "user", "content": text}],
                "model": "qwen-plus", # 假设默认模型为 qwen-plus，根据实际情况调整
                "stream": True # chat 接口通常支持流式传输
            }
            await test_api_latency(config_data["url"], "/chat", payload, f"{config_name} - /chat - {length_name}", is_stream=True)

    # 测试 /summarize_tongyi 接口
    print("\n======== 测试 /summarize_tongyi 接口 (文本总结) ========")
    for config_name, config_data in api_configs.items():
        if config_data["url"] == "http://your_online_api_url_here" or \
           config_data["url"] == "http://your_ngrok_local_api_url_here" or \
           config_data["url"] == TONGYI_ONLINE_BASE_URL and config_data["api_key"] == "sk-your_tongyi_api_key_here":
            print(f"跳过 {config_name}，因为URL或API Key未配置。")
            continue

        for length_name, length_type in text_lengths.items():
            text = generate_text(length_type)
            
            payload = {}
            endpoint = ""
            headers = {"Content-Type": "application/json"}
            is_stream_test = True # summarize_tongyi 和其内部调用都支持流式

            if config_data["is_proxy"]:
                # 调用代理服务器的 /summarize_tongyi 接口
                payload = {
                    "text": text,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "stream": True 
                }
                endpoint = "/summarize_tongyi"
                description_suffix = ""
            else:
                # 直接调用通义千问官方API (模拟 tongyi_chat_embedded 内部逻辑)
                payload = {
                    "model": "qwen-plus", 
                    "messages": [
                        {"role": "system", "content": "你是一个专业的通知总结专家，请根据通知内容总结，基于通知像人一样总结，更像朋友之间的聊天。"},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "stream": True,
                    "presence_penalty": 0.0,
                    "top_p": 1.0
                }
                endpoint = "/v1/chat/completions" # 通义千问兼容OpenAI的聊天接口
                headers["Authorization"] = f"Bearer {config_data['api_key']}"
                description_suffix = " (直接调用)"

            await test_api_latency(config_data["url"], endpoint, payload, 
                                   f"{config_name} - /summarize_tongyi{description_suffix} - {length_name}", 
                                   is_stream=is_stream_test, headers=headers)

    # 测试 /content 接口 (内容生成)
    print("\n======== 测试 /content 接口 (内容生成 - 代理服务器) ========")
    for config_name, config_data in api_configs.items():
        if not config_data["is_proxy"]: # /content 接口只测试代理服务器
            continue
        if config_data["url"] == "http://your_online_api_url_here" or config_data["url"] == "http://your_ngrok_local_api_url_here":
            print(f"跳过 {config_name}，因为URL未配置。")
            continue

        # Content 接口的输入是 `content`, `style`, `expection`。这里只关注 content 长度
        content_styles = [
            {"style": "新闻稿", "expection": "简洁明了，引人注目"},
            # 可以添加更多风格和效果
        ]
        
        for length_name, length_type in text_lengths.items():
            text = generate_text(length_type)
            for style_info in content_styles:
                payload = {
                    "content": text,
                    "style": style_info["style"],
                    "expection": style_info["expection"]
                }
                await test_api_latency(config_data["url"], "/content", payload, 
                                       f"{config_name} - /content - {length_name} ({style_info['style']})", is_stream=False)

    # 测试 /club_recommend 接口 (社团推荐)
    print("\n======== 测试 /club_recommend 接口 (社团推荐 - 代理服务器) ========")
    for config_name, config_data in api_configs.items():
        if not config_data["is_proxy"]: # /club_recommend 接口只测试代理服务器
            continue
        if config_data["url"] == "http://your_online_api_url_here" or config_data["url"] == "http://your_ngrok_local_api_url_here":
            print(f"跳过 {config_name}，因为URL未配置。")
            continue
        
        # 对于推荐接口，文本长度影响可能较小，主要看处理逻辑，所以只用一种长度的描述
        payload = {
            "User_name": "测试用户",
            "User_description": "喜欢阅读、户外运动和志愿服务，对计算机科学有浓厚兴趣。",
            "User_tags": ["阅读", "户外", "志愿", "编程"],
            "User_major": "计算机科学"
        }
        await test_api_latency(config_data["url"], "/club_recommend", payload, f"{config_name} - /club_recommend", is_stream=False)


if __name__ == "__main__":
    asyncio.run(main()) 