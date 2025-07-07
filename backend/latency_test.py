import requests
import time
import json
import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from config_manager import config
except ImportError:
    print("无法导入 config_manager。请确保 config_manager.py 文件存在。")
    # 如果config_manager不可用，提供一个模拟的config对象
    class MockConfig:
        def __init__(self):
            self.server_host = "127.0.0.1"
            self.server_port = 8000
            self.default_model = "Qwen/Qwen3-8B-AWQ" # 示例默认模型
    config = MockConfig()

# 从 vllm_proxy_server.py 和 summary.py 获取的通义千问 API 信息
TONGYI_API_KEY = "sk-354859a6d3ae438fb8ab9b98194f5266" # 请替换为您的真实API Key
TONGYI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

# 从 test_client_ngrok.py 获取的 ngrok 代理地址
NGROK_PROXY_URL = "https://6a52-125-220-159-5.ngrok-free.app" # 请替换为您的实际ngrok公网地址

# 定义不同的 max_tokens
DEFAULT_MAX_TOKENS = 16384

def call_tongyi_api_non_streaming(text_to_summarize):
    """直接调用通义千问 API 并测量延迟 (非流式响应)"""
    url = f"{TONGYI_BASE_URL}/chat/completions" # 通义千问的聊天完成接口
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TONGYI_API_KEY}"
    }
    payload = {
        "model": "qwen-plus", # 通义千问的模型名称
        "messages": [
            {"role": "system", "content": "你是一个专业的通知总结专家，请根据通知内容总结。"},
            {"role": "user", "content": text_to_summarize}
        ],
        "temperature": 0.7,
        "max_tokens": DEFAULT_MAX_TOKENS, # 使用新的max_tokens
        "top_p": 1.0,
        "stream": False # 非流式请求
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=90) # 增加超时时间
        response.raise_for_status() # 检查HTTP错误
        # 消耗响应内容，确保测量到完整延迟
        _ = response.json() 
        end_time = time.time()
        return end_time - start_time
    except requests.exceptions.RequestException as e:
        print(f"直接调用通义千问API (非流式) 失败: {e}")
        return None

def call_tongyi_api_streaming(prompt_text):
    """直接调用通义千问 API 并测量延迟 (流式响应)"""
    url = f"{TONGYI_BASE_URL}/chat/completions" # 通义千问的聊天完成接口
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TONGYI_API_KEY}"
    }
    payload = {
        "model": "qwen-plus", # 通义千问的模型名称
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.7,
        "max_tokens": DEFAULT_MAX_TOKENS, # 使用新的max_tokens
        "top_p": 1.0,
        "stream": True # 流式请求
    }
    
    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=120) # 增加超时时间
        response.raise_for_status() # 检查HTTP错误
        
        full_content = "" # 用于消耗所有流式数据
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                # 通义千问的流式响应没有 data: 前缀，直接是 JSON
                if decoded_chunk.strip() == "[DONE]": # 明确处理DONE标记
                    break
                if not decoded_chunk.strip():
                    continue # Skip empty lines
                try:
                    json_data = json.loads(decoded_chunk)
                    if json_data.get("choices") and len(json_data["choices"]) > 0:
                        delta = json_data["choices"][0].get("delta")
                        if delta and delta.get("content"): # 获取内容
                            full_content += delta["content"]
                except json.JSONDecodeError:
                    pass # 忽略非JSON或部分JSON的块

        end_time = time.time()
        return end_time - start_time
    except requests.exceptions.RequestException as e:
        print(f"直接调用通义千问API (流式) 失败: {e}")
        return None

def call_vllm_via_ngrok_proxy_streaming(prompt_text):
    """通过 ngrok 代理调用本地 vLLM 服务器的 /chat 接口并测量延迟 (流式响应)"""
    url = f"{NGROK_PROXY_URL}/chat" # 调用 ngrok 代理的 /chat 接口
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [
            {"role": "user", "content": prompt_text}
        ],
        "model": config.default_model, # 使用配置中的默认模型
        "max_tokens": DEFAULT_MAX_TOKENS, # 使用新的max_tokens
        "stream": True # 流式请求，以测量完整延迟
    }

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=120) # 增加超时时间
        response.raise_for_status() # 检查HTTP错误
        
        full_content = "" # 用于消耗所有流式数据
        for chunk in response.iter_lines():
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith("data:"):
                    data_content = decoded_chunk[5:].strip()
                    if data_content == "[DONE]":
                        break
                    if not data_content:
                        continue # Skip empty data lines
                    try:
                        json_data = json.loads(data_content)
                        if json_data.get("choices") and len(json_data["choices"]) > 0:
                            delta = json_data["choices"][0].get("delta")
                            if delta and delta.get("content"): # 获取内容
                                full_content += delta["content"]
                    except json.JSONDecodeError:
                        pass # 忽略非JSON或部分JSON的块

        end_time = time.time()
        return end_time - start_time
    except requests.exceptions.RequestException as e:
        print(f"通过ngrok代理调用vLLM服务器 (流式) 失败: {e}")
        return None

def call_vllm_via_ngrok_proxy_non_streaming(prompt_text):
    """通过 ngrok 代理调用本地 vLLM 服务器的 /simple_chat 接口并测量延迟 (非流式响应)"""
    url = f"{NGROK_PROXY_URL}/simple_chat" # 调用 ngrok 代理的 /simple_chat 接口
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt_text, # 使用prompt作为参数名
        "model": config.default_model, # 使用配置中的默认模型
        "max_tokens": DEFAULT_MAX_TOKENS, # 使用新的max_tokens
        "stream": False # 非流式请求，以测量完整延迟
    }

    start_time = time.time()
    try:
        response = requests.post(url, headers=headers, params=payload, timeout=90) # 增加超时时间
        response.raise_for_status() # 检查HTTP错误
        
        # 消耗响应内容，确保测量到完整延迟
        response_json = response.json()
        if "response" in response_json:
            _ = response_json["response"] # 获取实际回答内容
        
        end_time = time.time()
        return end_time - start_time
    except requests.exceptions.RequestException as e:
        print(f"通过ngrok代理调用vLLM服务器 (非流式) 失败: {e}")
        return None

def main():
    # 定义不同长度的测试文本
    short_text = "请用一句话介绍一下地球。"
    medium_text = (
        "标题：关于举办2024年春季运动会的通知\n\n"
        "各学院、各部门：\n\n"
        "为丰富校园文化生活，增强师生体质，经学校研究决定，定于2024年4月20日（星期六）"
        "在学校田径场举办春季运动会。现将有关事项通知如下：\n\n"
        "一、时间：2024年4月20日上午8:30\n"
        "二、地点：学校田径场\n"
        "三、参赛对象：全体在校师生\n"
        "四、比赛项目：\n"
        "  1. 学生组：100米、200米、400米、800米、1500米、4x100米接力、跳远、铅球\n"
        "  2. 教工组：100米、200米、4x100米接力、铅球、立定跳远\n"
        "五、报名方式：\n"
        "  1. 学生以学院为单位组织报名，请各学院体育委员于4月10日前将报名表电子版发送至体育部邮箱。\n"
        "  2. 教工以部门为单位组织报名，请各部门负责人于4月10日前将报名表纸质版报送至校工会。\n"
        "六、注意事项：\n"
        "  1. 请各单位加强宣传，积极组织师生参赛。\n"
        "  2. 参赛人员请提前做好准备活动，注意安全。\n"
        "  3. 运动会期间，请保持场地卫生，服从裁判安排。\n\n"
        "特此通知。\n\n"
        "学校体育运动委员会\n"
        "2024年4月1日"
    )
    # 假设一个较长的文本，这里用重复 medium_text 来模拟
    # 实际场景中可能需要一个真实的长文本或从文件中读取
    long_text = medium_text * 5 # 模拟长文本
    
    test_cases = {
        "短文本": short_text,
        "中等文本": medium_text,
        "长文本": long_text
    }

    num_runs = 3 # 运行次数
    
    all_results = {} # 存储所有测试用例的结果

    print(f"--- 开始延迟对比测试 ({num_runs} 次运行) ---")
    
    for text_type, sample_text in test_cases.items():
        print(f"\n{'='*10} 测试 {text_type} (长度: {len(sample_text)} 字符) {'='*10}")
        
        tongyi_non_streaming_latencies = []
        tongyi_streaming_latencies = []
        ngrok_vllm_streaming_latencies = []
        ngrok_vllm_non_streaming_latencies = []

        for i in range(num_runs):
            print(f"运行 {i+1}/{num_runs}...")
            
            # 直接调用通义千问 (非流式)
            latency = call_tongyi_api_non_streaming(sample_text)
            if latency is not None:
                tongyi_non_streaming_latencies.append(latency)
                print(f"  直接调用通义千问 API (非流式) 延迟: {latency:.4f} 秒")
            else:
                print("  直接调用通义千问 API (非流式) 失败")

            time.sleep(2) # 暂停

            # 直接调用通义千问 (流式)
            latency = call_tongyi_api_streaming(sample_text)
            if latency is not None:
                tongyi_streaming_latencies.append(latency)
                print(f"  直接调用通义千问 API (流式) 延迟: {latency:.4f} 秒")
            else:
                print("  直接调用通义千问 API (流式) 失败")

            time.sleep(2) # 暂停

            # 通过 ngrok 代理调用 vLLM 服务器 (流式)
            latency = call_vllm_via_ngrok_proxy_streaming(sample_text)
            if latency is not None:
                ngrok_vllm_streaming_latencies.append(latency)
                print(f"  通过 ngrok 代理调用 vLLM 服务器 (流式) 延迟: {latency:.4f} 秒")
            else:
                print("  通过 ngrok 代理调用 vLLM 服务器 (流式) 失败")
                
            time.sleep(2) # 暂停

            # 通过 ngrok 代理调用 vLLM 服务器 (非流式)
            latency = call_vllm_via_ngrok_proxy_non_streaming(sample_text)
            if latency is not None:
                ngrok_vllm_non_streaming_latencies.append(latency)
                print(f"  通过 ngrok 代理调用 vLLM 服务器 (非流式) 延迟: {latency:.4f} 秒")
            else:
                print("  通过 ngrok 代理调用 vLLM 服务器 (非流式) 失败")
            print("-" * 40)
        
        # 存储当前文本类型的测试结果
        all_results[text_type] = {
            "tongyi_non_streaming": tongyi_non_streaming_latencies,
            "tongyi_streaming": tongyi_streaming_latencies,
            "ngrok_vllm_streaming": ngrok_vllm_streaming_latencies,
            "ngrok_vllm_non_streaming": ngrok_vllm_non_streaming_latencies,
        }

    print("\n--- 所有测试结果总结 ---")
    for text_type, results in all_results.items():
        print(f"\n{'='*10} {text_type} 文本测试结果 {'='*10}")
        
        avg_tongyi_non_streaming = None
        if results["tongyi_non_streaming"]:
            avg_tongyi_non_streaming = sum(results["tongyi_non_streaming"]) / len(results["tongyi_non_streaming"])
            print(f"直接调用通义千问 API (非流式) 平均延迟: {avg_tongyi_non_streaming:.4f} 秒 ({len(results['tongyi_non_streaming'])} 次成功运行)")
        else:
            print("没有成功完成直接调用通义千问 API (非流式) 的测试。")

        avg_tongyi_streaming = None
        if results["tongyi_streaming"]:
            avg_tongyi_streaming = sum(results["tongyi_streaming"]) / len(results["tongyi_streaming"])
            print(f"直接调用通义千问 API (流式) 平均延迟: {avg_tongyi_streaming:.4f} 秒 ({len(results['tongyi_streaming'])} 次成功运行)")
            if avg_tongyi_non_streaming is not None:
                print(f"平均延迟差 (Tongyi 流式 - Tongyi 非流式): {(avg_tongyi_streaming - avg_tongyi_non_streaming):.4f} 秒")
        else:
            print("没有成功完成直接调用通义千问 API (流式) 的测试。")

        avg_ngrok_vllm_streaming = None
        if results["ngrok_vllm_streaming"]:
            avg_ngrok_vllm_streaming = sum(results["ngrok_vllm_streaming"]) / len(results["ngrok_vllm_streaming"])
            print(f"通过 ngrok 代理调用 vLLM 服务器 (流式) 平均延迟: {avg_ngrok_vllm_streaming:.4f} 秒 ({len(results['ngrok_vllm_streaming'])} 次成功运行)")
            if avg_tongyi_non_streaming is not None:
                print(f"平均延迟差 (ngrok-vLLM 流式 - Tongyi 非流式): {(avg_ngrok_vllm_streaming - avg_tongyi_non_streaming):.4f} 秒")
                
        else:
            print("没有成功完成通过 ngrok 代理调用 vLLM 服务器 (流式) 的测试。")

        avg_ngrok_vllm_non_streaming = None
        if results["ngrok_vllm_non_streaming"]:
            avg_ngrok_vllm_non_streaming = sum(results["ngrok_vllm_non_streaming"]) / len(results["ngrok_vllm_non_streaming"])
            print(f"通过 ngrok 代理调用 vLLM 服务器 (非流式) 平均延迟: {avg_ngrok_vllm_non_streaming:.4f} 秒 ({len(results['ngrok_vllm_non_streaming'])} 次成功运行)")
            if avg_tongyi_non_streaming is not None:
                print(f"平均延迟差 (ngrok-vLLM 非流式 - Tongyi 非流式): {(avg_ngrok_vllm_non_streaming - avg_tongyi_non_streaming):.4f} 秒")
        else:
            print("没有成功完成通过 ngrok 代理调用 vLLM 服务器 (非流式) 的测试。")
        
    print("\n注意：此处的延迟差是不同模型（通义千问 vs 本地vLLM）以及部署方式（云API vs 代理本地）的总和对比。")

    print("\n综合结论:")
    overall_fastest_method = ""
    overall_min_latency = float('inf')
    overall_tests_completed = True

    for text_type, results in all_results.items():
        text_type_latencies = []
        if results["tongyi_non_streaming"]: text_type_latencies.append((sum(results["tongyi_non_streaming"]) / len(results["tongyi_non_streaming"]), f"直接调用通义千问 API (非流式) [{text_type}]"))
        else: overall_tests_completed = False
        if results["tongyi_streaming"]: text_type_latencies.append((sum(results["tongyi_streaming"]) / len(results["tongyi_streaming"]), f"直接调用通义千问 API (流式) [{text_type}]"))
        else: overall_tests_completed = False
        if results["ngrok_vllm_streaming"]: text_type_latencies.append((sum(results["ngrok_vllm_streaming"]) / len(results["ngrok_vllm_streaming"]), f"通过 ngrok 代理调用 vLLM 服务器 (流式) [{text_type}]"))
        else: overall_tests_completed = False
        if results["ngrok_vllm_non_streaming"]: text_type_latencies.append((sum(results["ngrok_vllm_non_streaming"]) / len(results["ngrok_vllm_non_streaming"]), f"通过 ngrok 代理调用 vLLM 服务器 (非流式) [{text_type}]"))
        else: overall_tests_completed = False

        if text_type_latencies:
            fastest_for_type = min(text_type_latencies, key=lambda x: x[0])
            if fastest_for_type[0] < overall_min_latency:
                overall_min_latency = fastest_for_type[0]
                overall_fastest_method = fastest_for_type[1]
        else:
            overall_tests_completed = False # 如果某种文本类型的所有测试都失败了

    if overall_tests_completed:
        print(f"在所有测试用例中，最快的方法是: {overall_fastest_method} (平均延迟: {overall_min_latency:.4f} 秒)")
        print("请根据您的实际需求（如成本、模型性能、网络稳定性、是否需要流式输出等）选择合适的方案。")
    else:
        print("无法得出完整的综合结论，因为某些测试未能成功完成。请检查错误日志并确保所有服务运行正常。")

if __name__ == "__main__":
    main() 