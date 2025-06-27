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
    from config_manager import config
except ImportError as e:
    print(f"无法导入配置管理器: {e}")
    print("请确保config_manager.py文件存在且语法正确")
    sys.exit(1)

# 代理服务器配置
PROXY_SERVER_URL = f"http://{config.server_host}:{config.server_port}"

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
    """测试完整的聊天接口（非流式和流式）"""
    print("\n=== 测试完整聊天接口 (非流式) ===")
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "请用中文回答：什么是人工智能？"}
            ],
            "model": config.default_model,
            "max_tokens": 1500,
            "temperature": 0.7,
            "system_prompt": "你是一个有用的AI助手，请用中文回答问题。",
            "stream": False # 非流式
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
        
        non_stream_success = response.status_code == 200

    except Exception as e:
        print(f"非流式聊天错误: {e}")
        non_stream_success = False

    print("\n=== 测试完整聊天接口 (流式) ===")
    try:
        stream_payload = {
            "messages": [
                {"role": "user", "content": "请用中文回答：什么是区块链？"}
            ],
            "model": config.default_model,
            "max_tokens": 1500,
            "temperature": 0.7,
            "system_prompt": "你是一个有用的AI助手，请用中文回答问题。",
            "stream": True # 流式
        }

        print(f"发送流式请求: {stream_payload['messages'][0]['content']}")
        start_time = time.time()
        
        stream_response = requests.post(
            f"{PROXY_SERVER_URL}/chat",
            headers={"Content-Type": "application/json"},
            json=stream_payload, 
            stream=True
        )
        
        stream_response.raise_for_status() # 检查HTTP错误

        full_response_content = ""
        print("流式响应:")
        for chunk in stream_response.iter_lines(): # 使用iter_lines处理SSE
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith("data:"):
                    try:
                        json_data = json.loads(decoded_chunk[5:].strip())
                        if json_data.get("choices") and len(json_data["choices"]) > 0:
                            delta = json_data["choices"][0].get("delta")
                            if delta and delta.get("content"):
                                content = delta["content"]
                                print(content, end='')
                                full_response_content += content
                        elif "error" in json_data:
                            print(f"错误: {json_data['error']}")
                            stream_success = False
                            break
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from chunk: {decoded_chunk}")
                        # 打印原始数据，以防万一，但不计入full_response_content
                        print(decoded_chunk)
                elif decoded_chunk == "data: [DONE]": # 结束标记
                    break
                # 忽略其他非data开头的行，如空行或注释

        end_time = time.time()
        print(f"\n流式响应完成，响应时间: {end_time - start_time:.2f}秒")
        stream_success = True # 如果没有错误，则认为成功

    except Exception as e:
        print(f"流式聊天错误: {e}")
        stream_success = False
    
    return non_stream_success and stream_success

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

def test_generate_content():
    """测试AI内容生成接口"""
    print("\n=== 测试AI内容生成接口 ===")
    try:
        payload = {
            "content": "本周五晚7点，A栋101教室，举办Python入门讲座，面向全校师生",
            "style": "enthusiastic",
            "expection": "吸引更多人参与活动，激发读者热情"
        }
        
        print(f"发送生成内容请求，内容: {payload['content']}")
        start_time = time.time()
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/generate/content",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('generated_text')
            print(f"生成的文本:\n{generated_text}")
            return generated_text is not None and len(generated_text.strip()) > 0
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"AI内容生成测试错误: {e}")
        return False

def test_summarize_tongyi_streaming():
    """测试通义千问总结接口（流式）"""
    print("\n=== 测试通义千问总结接口 (流式) ===")
    try:
        text_to_summarize = (
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

        payload = {
            "text": text_to_summarize,
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1.0
        }

        print(f"发送总结请求，文本长度: {len(text_to_summarize)}")
        start_time = time.time()

        response = requests.post(
            f"{PROXY_SERVER_URL}/summarize_tongyi",
            headers={"Content-Type": "application/json"},
            json=payload,
            stream=True
        )

        response.raise_for_status() # 检查HTTP错误

        full_summary_content = ""
        print("流式总结响应:")
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                try:
                    decoded_chunk = chunk.decode('utf-8')
                    # 对于summarize_tongyi，响应可能是包含JSON的文本事件流，需要解析
                    if decoded_chunk.startswith("data:"): # EventSource 格式
                        try:
                            json_data = json.loads(decoded_chunk[5:].strip())
                            if "error" in json_data:
                                print(f"错误: {json_data['error']}")
                                return False
                            elif "summary" in json_data: # 完整的summary一次性返回
                                print(json_data["summary"], end='')
                                full_summary_content += json_data["summary"]
                            else: # 如果是分块返回的，直接打印
                                print(decoded_chunk, end='')
                                full_summary_content += decoded_chunk
                        except json.JSONDecodeError:
                            print(f"Warning: Could not decode JSON from chunk: {decoded_chunk}")
                            print(decoded_chunk, end='') # 打印原始数据，以防万一
                            full_summary_content += decoded_chunk
                    else:
                        print(decoded_chunk, end='')
                        full_summary_content += decoded_chunk
                except UnicodeDecodeError:
                    print(f"Warning: Could not decode chunk: {chunk}")

        end_time = time.time()
        print(f"\n流式总结完成，响应时间: {end_time - start_time:.2f}秒")
        
        if not full_summary_content.strip():
            print("通义千问流式总结返回空内容。")
            return False
        
        return True

    except Exception as e:
        print(f"通义千问流式总结错误: {e}")
        return False

def test_conversation():
    """测试多轮对话 (流式传输)"""
    print("\n=== 测试多轮对话 (流式传输) ===")
    try:
        # 第一轮对话
        payload1 = {
            "messages": [
                {"role": "user", "content": "你好，请用一句话介绍一下地球。"}
            ],
            "model": config.default_model,
            "max_tokens": 500,
            "stream": True # 流式传输
        }
        
        print("第一轮对话 (流式传输)...")
        start_time1 = time.time()
        response1 = requests.post(
            f"{PROXY_SERVER_URL}/chat",
            headers={"Content-Type": "application/json"},
            json=payload1,
            stream=True
        )
        
        response1.raise_for_status() # 检查HTTP错误

        full_response_content1 = ""
        print("助手回复 (第一轮):")
        for chunk in response1.iter_lines(): # 使用iter_lines处理SSE
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith("data:"):
                    try:
                        json_data = json.loads(decoded_chunk[5:].strip())
                        if json_data.get("choices") and len(json_data["choices"]) > 0:
                            delta = json_data["choices"][0].get("delta")
                            if delta and delta.get("content"):
                                content = delta["content"]
                                print(content, end='')
                                full_response_content1 += content
                        elif "error" in json_data:
                            print(f"错误: {json_data['error']}")
                            return False
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from chunk: {decoded_chunk}")
                        print(decoded_chunk) # 打印原始数据，以防万一
                elif decoded_chunk == "data: [DONE]": # 结束标记
                    break

        end_time1 = time.time()
        print(f"\n第一轮流式响应完成，响应时间: {end_time1 - start_time1:.2f}秒")
        assistant_response = full_response_content1.strip()
        
        if not assistant_response:
            print("第一轮对话流式响应为空，测试失败。")
            return False

        # 第二轮对话
        payload2 = {
            "messages": [
                {"role": "user", "content": "你好，我的名字是张三"},
                {"role": "assistant", "content": assistant_response},
                {"role": "user", "content": "你还记得我的名字吗？"}
            ],
            "model": config.default_model,
            "max_tokens": 500,
            "stream": True # 流式传输
        }
        
        print("\n第二轮对话 (流式传输)...")
        start_time2 = time.time()
        response2 = requests.post(
            f"{PROXY_SERVER_URL}/chat",
            headers={"Content-Type": "application/json"},
            json=payload2,
            stream=True
        )

        response2.raise_for_status() # 检查HTTP错误

        full_response_content2 = ""
        print("助手回复 (第二轮):")
        for chunk in response2.iter_lines(): # 使用iter_lines处理SSE
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk.startswith("data:"):
                    try:
                        json_data = json.loads(decoded_chunk[5:].strip())
                        if json_data.get("choices") and len(json_data["choices"]) > 0:
                            delta = json_data["choices"][0].get("delta")
                            if delta and delta.get("content"):
                                content = delta["content"]
                                print(content, end='')
                                full_response_content2 += content
                        elif "error" in json_data:
                            print(f"错误: {json_data['error']}")
                            return False
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from chunk: {decoded_chunk}")
                        print(decoded_chunk) # 打印原始数据，以防万一
                elif decoded_chunk == "data: [DONE]": # 结束标记
                    break

        end_time2 = time.time()
        print(f"\n第二轮流式响应完成，响应时间: {end_time2 - start_time2:.2f}秒")

        return True
            
    except Exception as e:
        print(f"流式多轮对话错误: {e}")
        return False

def test_generate_introduction():
    """测试AI社团介绍生成接口"""
    print("=== 测试AI社团介绍生成接口 ===")
    try:
        payload = {
            "content": "这是一个关于我们社团的草稿：我们是一个热爱编程的社团，经常组织编程比赛和技术分享。",
            "style": "humorous",
            "target_people": "新生，对编程感兴趣的同学"
        }
        
        print(f"发送生成社团介绍请求，内容: {payload['content']}")
        start_time = time.time()
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/generate/introduction",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('generated_text')
            print(f"生成的社团介绍: {generated_text}")
            return generated_text is not None and len(generated_text.strip()) > 0
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"AI社团介绍生成测试错误: {e}")
        return False

def test_generate_slogan():
    """测试AI社团口号生成接口"""
    print("=== 测试AI社团口号生成接口 ===")
    try:
        payload = {
            "theme": "编程社，创新，活力"
        }
        
        print(f"发送生成社团口号请求，主题: {payload['theme']}")
        start_time = time.time()
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/generate/Slogan",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('generated_text')
            print(f"生成的社团口号: {generated_text}")
            return generated_text is not None and len(generated_text.strip()) > 0
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"AI社团口号生成测试错误: {e}")
        return False

def main():
    """运行所有测试"""
    print("开始测试vLLM代理服务器...")
    print(f"服务器地址: {PROXY_SERVER_URL}")
    print(f"默认模型: {config.default_model}")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health_check),
        ("简化聊天", test_simple_chat),
        ("完整聊天", test_chat_completion),
        ("模型列表", test_models_list),
        ("配置信息", test_config_endpoint),
        ("AI内容生成", test_generate_content),
        ("通义总结 (流式)", test_summarize_tongyi_streaming),
        ("多轮对话", test_conversation),
        ("社团介绍生成", test_generate_introduction),
        ("社团口号生成", test_generate_slogan)
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
        print("⚠️  部分测试失败，请检查服务器配置和vLLM服务状态")

if __name__ == "__main__":
    main() 