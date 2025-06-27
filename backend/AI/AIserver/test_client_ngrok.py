import requests
import json
import time
import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    # 假设config_manager.py也在同一目录下
    from config_manager import config
except ImportError as e:
    print(f"无法导入配置管理器: {e}")
    print("请确保config_manager.py文件存在且语法正确")
    sys.exit(1)

# 代理服务器的ngrok公网地址
PROXY_SERVER_URL = "https://4e08-125-220-159-5.ngrok-free.app"

def test_health_check():
    """测试健康检查接口"""
    print("=== 测试健康检查接口 ===")
    try:
        response = requests.get(f"{PROXY_SERVER_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_simple_chat():
    """测试简化聊天接口"""
    print("\n=== 测试简化聊天接口 ===")
    try:
        prompt = "你好，请简单介绍一下自己"
        params = {
            "prompt": prompt,
            "model": config.default_model,
            "max_tokens": 1000
        }
        
        print(f"发送请求: {prompt}")
        start_time = time.time()
        
        response = requests.post(f"{PROXY_SERVER_URL}/simple_chat", params=params)
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"模型: {result.get('model')}")
            print(f"响应: {result.get('response')}")
        else:
            print(f"错误响应: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_chat_completion():
    """测试完整的聊天接口"""
    print("\n=== 测试完整聊天接口 ===")
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "请用中文回答：什么是人工智能？"}
            ],
            "model": config.default_model,
            "max_tokens": 1500,
            "temperature": 0.7,
            "system_prompt": "你是一个有用的AI助手，请用中文回答问题。"
        }
        
        print(f"发送请求: {payload['messages'][0]['content']}")
        start_time = time.time()
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/chat",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"模型: {result.get('model')}")
            print(f"响应: {result.get('response')}")
            if result.get('usage'):
                print(f"使用情况: {result.get('usage')}")
        else:
            print(f"错误响应: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_models_list():
    """测试模型列表接口"""
    print("\n=== 测试模型列表接口 ===")
    try:
        response = requests.get(f"{PROXY_SERVER_URL}/models")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"可用模型: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_config_endpoint():
    """测试配置信息接口"""
    print("\n=== 测试配置信息接口 ===")
    try:
        response = requests.get(f"{PROXY_SERVER_URL}/config")
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"服务器配置: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_tongyi_summary():
    """测试通义千问总结接口"""
    print("\n=== 测试通义千问总结接口 ===")
    test_text = "今天天气晴朗，阳光明媚，非常适合户外活动。公园里挤满了人，有的在慢跑，有的在打羽毛球，还有许多小朋友在操场上玩耍，欢声笑语不绝于耳。这是一个令人感到愉快的周末。"
    try:
        payload = {
            "text": test_text,
            "temperature": 0.7
        }
        print(f"发送总结请求: {test_text[:50]}...")
        start_time = time.time()
        response = requests.post(
            f"{PROXY_SERVER_URL}/summarize_tongyi",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        if response.status_code == 200:
            result = response.json()
            print(f"总结结果: {result.get('summary')}")
        else:
            print(f"错误响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"错误: {e}")
        return False

def test_conversation():
    """测试多轮对话"""
    print("\n=== 测试多轮对话 ===")
    try:
        # 第一轮对话
        payload1 = {
            "messages": [
                {"role": "user", "content": "你好，我的名字是张三"}
            ],
            "model": config.default_model,
            "max_tokens": 500
        }
        
        print("第一轮对话...")
        response1 = requests.post(
            f"{PROXY_SERVER_URL}/chat",
            headers={"Content-Type": "application/json"},
            json=payload1
        )
        
        if response1.status_code != 200:
            print(f"第一轮对话失败: {response1.text}")
            return False
        
        result1 = response1.json()
        assistant_response = result1.get('response')
        print(f"助手回复: {assistant_response}")
        
        # 第二轮对话
        payload2 = {
            "messages": [
                {"role": "user", "content": "你好，我的名字是张三"},
                {"role": "assistant", "content": assistant_response},
                {"role": "user", "content": "你还记得我的名字吗？"}
            ],
            "model": config.default_model,
            "max_tokens": 500
        }
        
        print("第二轮对话...")
        response2 = requests.post(
            f"{PROXY_SERVER_URL}/chat",
            headers={"Content-Type": "application/json"},
            json=payload2
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"助手回复: {result2.get('response')}")
            return True
        else:
            print(f"第二轮对话失败: {response2.text}")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试vLLM代理服务器 (ngrok 公网地址)...")
    print(f"服务器地址: {PROXY_SERVER_URL}")
    print(f"默认模型: {config.default_model}")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health_check),
        ("简化聊天", test_simple_chat),
        ("完整聊天", test_chat_completion),
        ("模型列表", test_models_list),
        ("配置信息", test_config_endpoint),
        ("通义总结", test_tongyi_summary),
        ("多轮对话", test_conversation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
            print(f"{test_name}: {'✓ 通过' if success else '✗ 失败'}")
        except Exception as e:
            print(f"{test_name}: ✗ 异常 - {e}")
            results.append((test_name, False))
        
        print("-" * 30)
        time.sleep(1)  # 避免请求过于频繁
    
    # 总结测试结果
    print("\n=== 测试总结 ===")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！")
    else:
        print("⚠️  部分测试失败，请检查服务器配置和ngrok服务状态")

if __name__ == "__main__":
    main() 