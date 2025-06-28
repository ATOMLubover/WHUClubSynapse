import requests
import json
import time
import os
import sys
from openai import OpenAI

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from config_manager import config
except ImportError as e:
    print(f"无法导入配置管理器: {e}")
    print("请确保config_manager.py文件存在且语法正确")
    sys.exit(1)

# --- 配置 ---
# 通义API直连配置 (从 vllm_proxy_server.py 获取)
TONGYI_API_KEY = "sk-354859a6d3ae438fb8ab9b98194f5266"
TONGYI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
TONGYI_MODEL = "qwen-plus" # 通义API使用的模型

# ngrok代理服务器配置 (从 test_client_ngrok.py 获取)
NGROK_PROXY_URL = "https://13a8-125-220-159-5.ngrok-free.app"
DEFAULT_MODEL = config.default_model # 从 config_manager 获取默认模型

TEST_PROMPT_SHORT = "请用一句话介绍人工智能。"
TEST_PROMPT_LONG = "请详细介绍人工智能的起源、发展、主要技术（如机器学习、深度学习、自然语言处理等）、应用领域、面临的挑战以及未来展望。请确保内容丰富，字数在500字以上。"
NUM_ITERATIONS = 5 # 每个测试场景的运行次数

def calculate_average(times):
    """计算平均时间"""
    if not times:
        return 0
    return sum(times) / len(times)

def run_test_scenario(name, test_func, prompt, is_streaming=False):
    """运行一个测试场景并收集响应时间"""
    print(f"\n=== 运行 {name} 测试 ({'流式' if is_streaming else '非流式'}) ===")
    times = []
    for i in range(NUM_ITERATIONS):
        print(f"  - 第 {i+1}/{NUM_ITERATIONS} 次测试...")
        try:
            start_time = time.time()
            full_response_content = test_func(prompt)
            end_time = time.time()
            response_time = end_time - start_time
            times.append(response_time)
            print(f"    响应时间: {response_time:.2f}秒")
            if not is_streaming and full_response_content:
                print(f"    响应长度: {len(full_response_content)} 字符")
            elif is_streaming:
                print(f"    流式内容接收完成。")
        except Exception as e:
            print(f"    测试失败: {e}")
            times.append(float('inf')) # 标记为失败，不计入平均
    
    avg_time = calculate_average([t for t in times if t != float('inf')])
    print(f"--- {name} 平均响应时间: {avg_time:.2f}秒 (成功 {len([t for t in times if t != float('inf')])}/{NUM_ITERATIONS} 次) ---")
    return times

# --- 通义API直连测试函数 ---
def test_tongyi_non_stream_chat(prompt):
    """直接调用通义API进行非流式聊天"""
    client = OpenAI(api_key=TONGYI_API_KEY, base_url=TONGYI_BASE_URL)
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(
        model=TONGYI_MODEL,
        messages=messages,
        stream=False,
        temperature=0.7,
        max_tokens=2000
    )
    return completion.choices[0].message.content

def test_tongyi_stream_chat(prompt):
    """直接调用通义API进行流式聊天"""
    client = OpenAI(api_key=TONGYI_API_KEY, base_url=TONGYI_BASE_URL)
    messages = [{"role": "user", "content": prompt}]
    full_response_content = ""
    completion = client.chat.completions.create(
        model=TONGYI_MODEL,
        messages=messages,
        stream=True,
        temperature=0.7,
        max_tokens=2000
    )
    for chunk in completion:
        if chunk.choices[0].delta.content:
            full_response_content += chunk.choices[0].delta.content
    return full_response_content

# --- ngrok代理本地vLLM测试函数 ---
def test_ngrok_non_stream_chat(prompt):
    """通过ngrok代理调用本地vLLM进行非流式聊天"""
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": DEFAULT_MODEL,
        "max_tokens": 2000,
        "temperature": 0.7,
        "stream": False
    }
    response = requests.post(
        f"{NGROK_PROXY_URL}/chat",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    response.raise_for_status()
    return response.json().get("response")

def test_ngrok_stream_chat(prompt):
    """通过ngrok代理调用本地vLLM进行流式聊天"""
    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": DEFAULT_MODEL,
        "max_tokens": 2000,
        "temperature": 0.7,
        "stream": True
    }
    full_response_content = ""
    response = requests.post(
        f"{NGROK_PROXY_URL}/chat",
        headers={"Content-Type": "application/json"},
        json=payload,
        stream=True
    )
    response.raise_for_status()
    for chunk in response.iter_lines():
        if chunk:
            decoded_chunk = chunk.decode('utf-8')
            if decoded_chunk == "data: [DONE]": # 结束标记
                break
            elif decoded_chunk.startswith("data:"):
                try:
                    json_data = json.loads(decoded_chunk[5:].strip())
                    if json_data.get("choices") and len(json_data["choices"]) > 0:
                        delta = json_data["choices"][0].get("delta")
                        if delta and delta.get("content"):
                            full_response_content += delta["content"]
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from chunk: {decoded_chunk}")
    return full_response_content

def main():
    """主函数，运行所有性能测试"""
    print("🚀 开始运行性能测试...")
    print(f"每个测试场景运行 {NUM_ITERATIONS} 次")
    print(f"ngrok代理地址: {NGROK_PROXY_URL}")
    print(f"默认模型 (ngrok): {DEFAULT_MODEL}")
    print(f"通义API地址: {TONGYI_BASE_URL}")
    print(f"通义模型: {TONGYI_MODEL}")
    print("=" * 60)

    # 短文本测试
    print("\n### 短文本测试 ###")
    run_test_scenario("通义直连", test_tongyi_non_stream_chat, TEST_PROMPT_SHORT, is_streaming=False)
    run_test_scenario("通义直连", test_tongyi_stream_chat, TEST_PROMPT_SHORT, is_streaming=True)
    run_test_scenario("ngrok代理", test_ngrok_non_stream_chat, TEST_PROMPT_SHORT, is_streaming=False)
    run_test_scenario("ngrok代理", test_ngrok_stream_chat, TEST_PROMPT_SHORT, is_streaming=True)

    # 长文本测试
    print("\n### 长文本测试 ###")
    run_test_scenario("通义直连", test_tongyi_non_stream_chat, TEST_PROMPT_LONG, is_streaming=False)
    run_test_scenario("通义直连", test_tongyi_stream_chat, TEST_PROMPT_LONG, is_streaming=True)
    run_test_scenario("ngrok代理", test_ngrok_non_stream_chat, TEST_PROMPT_LONG, is_streaming=False)
    run_test_scenario("ngrok代理", test_ngrok_stream_chat, TEST_PROMPT_LONG, is_streaming=True)

    print("\n✅ 性能测试完成！")

if __name__ == "__main__":
    main() 