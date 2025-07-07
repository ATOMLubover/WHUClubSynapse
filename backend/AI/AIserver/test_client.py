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
            f"{PROXY_SERVER_URL}/content",
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
        for chunk in response.iter_lines(): # 使用iter_lines处理SSE
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                if decoded_chunk == "data: [DONE]": # 结束标记
                    break
                elif decoded_chunk.startswith("data:"):
                    try:
                        json_data = json.loads(decoded_chunk[5:].strip())
                        if "error" in json_data:
                            print(f"错误: {json_data['error']}")
                            stream_success = False
                            break
                        elif "summary" in json_data: # 完整的summary一次性返回
                            content = json_data["summary"]
                            print(content, end='')
                            full_summary_content += content
                        else: # 如果是分块返回的，直接打印
                            print(decoded_chunk, end='')
                            full_summary_content += decoded_chunk
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from chunk: {decoded_chunk}")
                        # 打印原始数据，以防万一，但不计入full_response_content
                        print(decoded_chunk)
                # 忽略其他非data开头的行，如空行或注释

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
            f"{PROXY_SERVER_URL}/introduction",
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
            f"{PROXY_SERVER_URL}/Slogan",
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

def test_reload_config():
    """测试配置重载接口"""
    print("\n=== 测试配置重载接口 ===")
    try:
        response = requests.get(f"{PROXY_SERVER_URL}/reload_config")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200 and response.json().get("status") == "success"
    except Exception as e:
        print(f"配置重载测试错误: {e}")
        return False

def test_screen_application():
    """测试智能申请筛选助手接口"""
    print("\n=== 测试智能申请筛选助手接口 ===")
    try:
        payload = {
            "applicant_data": {
                "name": "李华",
                "major": "计算机科学与技术",
                "skills": ["Python编程", "数据结构", "Web开发"],
                "experience": "曾参与校内编程竞赛并获得二等奖"
            },
            "application_reason": "我对贵社团的编程氛围和技术挑战非常感兴趣，希望能在社团中提升自己的编程能力并结识志同道合的朋友。我熟悉Python语言，并有Web开发经验。",
            "required_conditions": ["有编程基础", "对算法有兴趣", "积极参与团队项目"],
            "club_name": "编程社"
        }
        
        print(f"发送申请筛选请求，申请人: {payload['applicant_data']['name']}")
        start_time = time.time()
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/screen_application",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            summary = result.get('summary')
            suggestion = result.get('suggestion')
            print(f"AI摘要:\n{summary}")
            print(f"AI建议:\n{suggestion}")
            return summary is not None and suggestion is not None and len(summary.strip()) > 0 and len(suggestion.strip()) > 0
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"智能申请筛选助手测试错误: {e}")
        return False

def test_club_atmosphere():
    """测试社团氛围透视镜接口"""
    print("\n=== 测试社团氛围透视镜接口 ===")
    try:
        payload = {
            "communication_content": (
                "社团成员A: 今天的编程挑战太难了，我卡住了！\n"
                "社团成员B: 别灰心，我来帮你看看！我们可以一起调试。\n"
                "社团成员C: 对，大家多交流，互相帮助才能进步！\n"
                "社团成员D: 最近有个新算法很有意思，有空我给大家分享一下。\n"
                "社团成员E: 期待！正好最近在研究这方面的东西。\n"
                "社团管理员: 下周五有一次线下技术交流会，欢迎大家积极参加！"
            )
        }
        
        print(f"发送社团氛围透视请求，内容长度: {len(payload['communication_content'])}")
        start_time = time.time()
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/club_atmosphere",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            atmosphere_tags = result.get('atmosphere_tags')
            culture_summary = result.get('culture_summary')
            print(f"AI氛围标签: {atmosphere_tags}")
            print(f"AI文化摘要:\n{culture_summary}")
            return (atmosphere_tags is not None and isinstance(atmosphere_tags, list) and len(atmosphere_tags) > 0 and 
                    culture_summary is not None and len(culture_summary.strip()) > 0)
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"社团氛围透视测试错误: {e}")
        return False

def test_plan_event():
    """
    测试智能活动策划参谋接口
    """
    print("\n=== 测试智能活动策划参谋接口 ===")
    try:
        payload = {
            "event_idea": "我们想为50人办一场户外烧烤"
        }
        
        print(f"发送活动策划请求，想法: {payload['event_idea']}")
        start_time = time.time()
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/plan_event",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            checklist = result.get('checklist')
            budget_estimate = result.get('budget_estimate')
            risk_assessment = result.get('risk_assessment')
            creative_ideas = result.get('creative_ideas')
            
            print(f"策划清单:\n{json.dumps(checklist, indent=2, ensure_ascii=False)}")
            print(f"预算估算:\n{budget_estimate}")
            print(f"风险评估与预案:\n{risk_assessment}")
            print(f"创意点子:\n{json.dumps(creative_ideas, indent=2, ensure_ascii=False)}")
            
            return (checklist is not None and len(checklist) > 0 and
                    budget_estimate is not None and len(budget_estimate.strip()) > 0 and
                    risk_assessment is not None and len(risk_assessment.strip()) > 0 and
                    creative_ideas is not None and len(creative_ideas) > 0)
        else:
            print(f"错误响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"智能活动策划测试错误: {e}")
        return False

def test_financial_bookkeeping():
    """
    测试智能财务助理 - 对话式记账接口
    """
    print("\n=== 测试智能财务助理 - 对话式记账接口 ===")
    try:
        payload = {
            "natural_language_input": "今天活动买了10瓶水和一包零食，一共花了55.8元，从小明那里报销。",
            "club_name": "篮球社" # 新增社团名称
        }

        print(f"发送记账请求 (社团: {payload['club_name']}): {payload['natural_language_input']}")
        start_time = time.time()

        response = requests.post(
            f"{PROXY_SERVER_URL}/financial_bookkeeping",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")

        if response.status_code == 200:
            result = response.json()
            parsed_entries = result.get('parsed_entries')
            confirmation_message = result.get('confirmation_message')
            original_input = result.get('original_input')

            print(f"解析出的条目:\n{json.dumps(parsed_entries, indent=2, ensure_ascii=False)}")
            print(f"确认信息:\n{confirmation_message}")
            print(f"原始输入:\n{original_input}")

            # 验证响应内容
            return (parsed_entries is not None and isinstance(parsed_entries, list) and len(parsed_entries) > 0 and
                    confirmation_message is not None and len(confirmation_message.strip()) > 0 and
                    original_input == payload["natural_language_input"])
        else:
            print(f"错误响应: {response.text}")
            return False

    except Exception as e:
        print(f"智能财务助理 - 对话式记账测试错误: {e}")
        return False

def test_generate_financial_report():
    """
    测试智能财务助理 - 一键生成财务报表接口
    """
    print("\n=== 测试智能财务助理 - 一键生成财务报表接口 ===")
    try:
        club_name = "篮球社" # 指定要生成报表的社团名称
        payload = {
            "club_name": club_name
        }

        print(f"发送财务报表生成请求 (社团: {club_name})")
        start_time = time.time()

        response = requests.post(
            f"{PROXY_SERVER_URL}/generate_financial_report",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")

        if response.status_code == 200:
            result = response.json()
            report_summary = result.get('report_summary')
            expense_breakdown = result.get('expense_breakdown')
            income_breakdown = result.get('income_breakdown')

            print(f"报表总结:\n{report_summary}")
            print(f"支出分类:\n{json.dumps(expense_breakdown, indent=2, ensure_ascii=False)}")
            print(f"收入分类:\n{json.dumps(income_breakdown, indent=2, ensure_ascii=False)}")

            # 验证响应内容
            return (response.status_code == 200 and 
                    report_summary is not None and len(report_summary.strip()) > 0 and
                    expense_breakdown is not None and isinstance(expense_breakdown, dict) and
                    income_breakdown is not None and isinstance(income_breakdown, dict))
        else:
            print(f"错误响应: {response.text}")
            return False

    except Exception as e:
        print(f"智能财务助理 - 财务报表生成测试错误: {e}")
        return False

def test_update_budget():
    """
    测试智能财务助理 - 修改预算接口
    """
    print("\n=== 测试智能财务助理 - 修改预算接口 ===")
    try:
        club_name = "篮球社"
        new_budget = 2000.00
        budget_desc = "篮球社2024年全年预算"
        payload = {
            "club_name": club_name,
            "new_budget_limit": new_budget,
            "budget_description": budget_desc
        }

        print(f"发送修改预算请求 (社团: {club_name}, 新预算: {new_budget})")
        start_time = time.time()

        response = requests.post(
            f"{PROXY_SERVER_URL}/update_budget",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        end_time = time.time()
        print(f"状态码: {response.status_code}")
        print(f"响应时间: {end_time - start_time:.2f}秒")

        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return (result.get("message") == f"{club_name} 的预算已成功更新" and
                    result.get("club_name") == club_name and
                    result.get("new_budget_limit") == new_budget and
                    result.get("budget_description") == budget_desc)
        else:
            print(f"错误响应: {response.text}")
            return False

    except Exception as e:
        print(f"智能财务助理 - 修改预算测试错误: {e}")
        return False

def test_budget_warning():
    """
    测试智能财务助理 - 预算超支预警接口
    """
    print("\n=== 测试智能财务助理 - 预算超支预警接口 ===")
    try:
        club_name = "篮球社" # 指定社团名称
        # 场景1: 支出在预算内
        payload1 = {
            "current_spending": 800.00,
            "budget_limit": 1000.00, # 临时预算，可覆盖存储的社团预算
            "description": "春季游园会",
            "club_name": club_name
        }

        print(f"发送预算预警请求 (场景1: {club_name}, 800/1000): {payload1['description']}")
        start_time1 = time.time()
        response1 = requests.post(
            f"{PROXY_SERVER_URL}/budget_warning",
            headers={"Content-Type": "application/json"},
            json=payload1
        )
        end_time1 = time.time()
        print(f"状态码: {response1.status_code}")
        print(f"响应时间: {end_time1 - start_time1:.2f}秒")
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"预警信息:\n{result1.get('warning_message')}")
            print(f"是否超预算: {result1.get('is_over_budget')}")
            print(f"预算使用百分比: {result1.get('percentage_used'):.2f}%")
            test1_success = (result1.get('warning_message') is not None and 
                             isinstance(result1.get('is_over_budget'), bool) and 
                             not result1.get('is_over_budget') and 
                             isinstance(result1.get('percentage_used'), (float, int)) and 
                             result1.get('percentage_used') > 0)
        else:
            print(f"错误响应: {response1.text}")
            test1_success = False
        
        time.sleep(1) # 暂停避免请求过快

        # 场景2: 支出超预算 (使用存储的社团预算，先通过update_budget设置)
        # 假设在运行此测试前，篮球社的预算已经通过test_update_budget设置为2000
        payload2 = {
            "current_spending": 2100.00,
            "description": "夏季迎新活动",
            "club_name": club_name # 使用已存储的社团预算
        }

        print(f"\n发送预算预警请求 (场景2: {club_name}, 2100/2000): {payload2['description']}")
        start_time2 = time.time()
        response2 = requests.post(
            f"{PROXY_SERVER_URL}/budget_warning",
            headers={"Content-Type": "application/json"},
            json=payload2
        )
        end_time2 = time.time()
        print(f"状态码: {response2.status_code}")
        print(f"响应时间: {end_time2 - start_time2:.2f}秒")
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"预警信息:\n{result2.get('warning_message')}")
            print(f"是否超预算: {result2.get('is_over_budget')}")
            print(f"预算使用百分比: {result2.get('percentage_used'):.2f}%")
            test2_success = (result2.get('warning_message') is not None and 
                             isinstance(result2.get('is_over_budget'), bool) and 
                             result2.get('is_over_budget') and 
                             isinstance(result2.get('percentage_used'), (float, int)) and 
                             result2.get('percentage_used') > 100)
        else:
            print(f"错误响应: {response2.text}")
            test2_success = False

        # 场景3: 社团未设置预算，且请求中未提供预算
        payload3 = {
            "current_spending": 100.00,
            "description": "测试无预算社团",
            "club_name": "不存在的社团" # 使用一个不存在的社团名
        }
        print(f"\n发送预算预警请求 (场景3: 不存在社团，无预算): {payload3['description']}")
        start_time3 = time.time()
        response3 = requests.post(
            f"{PROXY_SERVER_URL}/budget_warning",
            headers={"Content-Type": "application/json"},
            json=payload3
        )
        end_time3 = time.time()
        print(f"状态码: {response3.status_code}")
        print(f"响应时间: {end_time3 - start_time3:.2f}秒")
        if response3.status_code == 400:
            print(f"预期错误响应: {response3.text}")
            test3_success = True # 预期返回400，表示成功测试了错误情况
        else:
            print(f"错误响应: {response3.text}")
            test3_success = False

        return test1_success and test2_success and test3_success

    except Exception as e:
        print(f"智能财务助理 - 预算超支预警测试错误: {e}")
        return False

def test_generate_activity_post():
    """测试社团动态总结生成接口"""
    print("\n=== 测试社团动态总结生成 ===")
    
    url = f"{PROXY_SERVER_URL}/generate/activity_post"
    
    # 测试用例1：文艺活动总结
    payload = {
        "content": """吉他社"弦音之夜"音乐分享会
时间：2024年3月15日晚7点-9点
地点：学生活动中心音乐厅
参与人数：约80人
活动过程：
1. 开场由社长带来一首《海阔天空》
2. 6组同学进行了原创音乐展示
3. 举办了即兴吉他弹唱互动环节
4. 进行了乐器保养知识分享

活动亮点：
- 原创歌曲《校园晚风》获得热烈反响
- 多名新成员首次登台表演
- 现场观众积极参与互动环节

参与者反馈：
- "第一次在台上表演，很紧张但很快乐"
- "学到了很多吉他保养知识"
- "期待下次活动"

后续计划：
每月举办一次主题音乐分享会""",
        "style": "温暖真诚",
        "expection": "展现活动温暖氛围，吸引更多音乐爱好者加入"
    }
    
    print("发送请求...")
    print(f"活动内容: {payload['content'][:100]}...")
    print(f"期望文风: {payload['style']}")
    print(f"期望效果: {payload['expection']}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print("\n生成结果:")
        print(result["generated_text"])
        print("\n请求成功 ✓")
    except Exception as e:
        print(f"\n请求失败: {str(e)} ✗")
        return False
    
    # 测试用例2：学术活动总结
    payload = {
        "content": """Python编程竞赛总结
时间：2024年3月25日14:00-17:00
地点：第一教学楼机房
参与人数：42人

比赛过程：
1. 分为初级和高级两个组别
2. 共设计10道算法题目
3. 3小时比赛时间
4. 设立多个奖项

活动亮点：
- 新生王同学以满分成绩获得初级组冠军
- 高级组产生3个优秀解法
- 参赛者普遍反映题目设计合理

参与者反馈：
- "题目难度递进，很适合学习"
- "比赛平台很专业"
- "希望能多举办类似比赛"

数据统计：
- 平均完成题目数：6道
- 满分人数：2人
- 参与年级：大一至大四

后续计划：
每学期举办两次编程竞赛""",
        "style": "专业严谨",
        "expection": "展示比赛专业性和含金量"
    }
    
    print("\n发送第二个请求...")
    print(f"活动内容: {payload['content'][:100]}...")
    print(f"期望文风: {payload['style']}")
    print(f"期望效果: {payload['expection']}")
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        print("\n生成结果:")
        print(result["generated_text"])
        print("\n请求成功 ✓")
        return True
    except Exception as e:
        print(f"\n请求失败: {str(e)} ✗")
        return False

def test_generate_ml_data():
    """测试机器学习数据生成接口"""
    print("\n=== 测试机器学习数据生成 ===")
    try:
        # 测试用例1: 生成少量数据
        payload1 = {
            "num_communities": 3,
            "num_users": 3,
            "num_interactions": 5,
            "save_file": "ml_data_test_small.json"
        }
        
        print(f"发送请求 (少量数据): {payload1}")
        start_time1 = time.time()
        response1 = requests.post(
            f"{PROXY_SERVER_URL}/generate_ml_data",
            headers={"Content-Type": "application/json"},
            json=payload1
        )
        end_time1 = time.time()
        print(f"状态码: {response1.status_code}")
        print(f"响应时间: {end_time1 - start_time1:.2f}秒")
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"生成消息: {result1.get('message')}")
            print(f"保存路径: {result1.get('file_path')}")
            print(f"社团数量: {len(result1.get('communities', []))}")
            print(f"用户数量: {len(result1.get('users', []))}")
            print(f"互动数量: {len(result1.get('interactions', []))}")
            test1_success = (len(result1.get('communities', [])) >= payload1["num_communities"] and
                             len(result1.get('users', [])) >= payload1["num_users"] and
                             len(result1.get('interactions', [])) >= payload1["num_interactions"])
        else:
            print(f"错误响应: {response1.text}")
            test1_success = False

        time.sleep(1) # 暂停避免请求过快

        # 测试用例2: 生成更多数据 (不保存文件)
        payload2 = {
            "num_communities": 5,
            "num_users": 5,
            "num_interactions": 10,
            "save_file": None
        }
        
        print(f"\n发送请求 (更多数据，不保存): {payload2}")
        start_time2 = time.time()
        response2 = requests.post(
            f"{PROXY_SERVER_URL}/generate_ml_data",
            headers={"Content-Type": "application/json"},
            json=payload2
        )
        end_time2 = time.time()
        print(f"状态码: {response2.status_code}")
        print(f"响应时间: {end_time2 - start_time2:.2f}秒")
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"生成消息: {result2.get('message')}")
            print(f"保存路径: {result2.get('file_path')}")
            print(f"社团数量: {len(result2.get('communities', []))}")
            print(f"用户数量: {len(result2.get('users', []))}")
            print(f"互动数量: {len(result2.get('interactions', []))}")
            test2_success = (len(result2.get('communities', [])) >= payload2["num_communities"] and
                             len(result2.get('users', [])) >= payload2["num_users"] and
                             len(result2.get('interactions', [])) >= payload2["num_interactions"] and
                             result2.get('file_path') is None)
        else:
            print(f"错误响应: {response2.text}")
            test2_success = False

        return test1_success and test2_success

    except Exception as e:
        print(f"机器学习数据生成测试错误: {e}")
        return False

def test_club_recommend():
    """测试社团推荐接口"""
    print("\n=== 测试社团推荐接口 ===")
    try:
        # 测试用例1：普通学生
        payload = {
            "User_name": "张三",
            "User_description": "我是一名大一新生，喜欢编程和摄影，希望能在课余时间提升自己的技能，结交志同道合的朋友。",
            "User_tags": ["编程", "摄影", "技术", "交友"],
            "User_major": "计算机科学与技术"
        }
        
        print("发送推荐请求...")
        print(f"用户名: {payload['User_name']}")
        print(f"用户描述: {payload['User_description']}")
        print(f"用户标签: {payload['User_tags']}")
        print(f"专业: {payload['User_major']}")
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/club_recommend",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n推荐结果:")
            print(f"总结文本: {result['Summary_text']}")
            print("\n推荐社团列表:")
            for club in result['Recommend_club_list']:
                print(f"\n社团名称: {club['club_name']}")
                print(f"描述: {club['description']}")
                print(f"标签: {club['tags']}")
                print(f"推荐理由: {club['recommend_reason']}")
            test1_success = True
        else:
            print(f"错误响应: {response.text}")
            test1_success = False
            
        time.sleep(1)  # 避免请求过快
        
        # 测试用例2：特殊兴趣学生
        payload = {
            "User_name": "李四",
            "User_description": "我对人工智能和机器学习非常感兴趣，同时也喜欢参加志愿者活动。希望能找到既能提升专业能力，又能服务社会的社团。",
            "User_tags": ["AI", "机器学习", "志愿服务", "社会实践"],
            "User_major": "人工智能"
        }
        
        print("\n发送第二个推荐请求...")
        print(f"用户名: {payload['User_name']}")
        print(f"用户描述: {payload['User_description']}")
        print(f"用户标签: {payload['User_tags']}")
        print(f"专业: {payload['User_major']}")
        
        response = requests.post(
            f"{PROXY_SERVER_URL}/club_recommend",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n推荐结果:")
            print(f"总结文本: {result['Summary_text']}")
            print("\n推荐社团列表:")
            for club in result['Recommend_club_list']:
                print(f"\n社团名称: {club['club_name']}")
                print(f"描述: {club['description']}")
                print(f"标签: {club['tags']}")
                print(f"推荐理由: {club['recommend_reason']}")
            test2_success = True
        else:
            print(f"错误响应: {response.text}")
            test2_success = False
            
        return test1_success and test2_success
        
    except Exception as e:
        print(f"社团推荐测试错误: {e}")
        return False

def main():
    """
    运行所有测试
    """
    print("开始测试vLLM代理服务器...")
    print(f"服务器地址: {PROXY_SERVER_URL}")
    print(f"默认模型: {config.default_model}")
    print("=" * 50)
    
    tests = [
        ("健康检查", test_health_check),
        ("简化聊天", test_simple_chat),
        # ("完整聊天", test_chat_completion),
        # ("模型列表", test_models_list),
        # ("配置信息", test_config_endpoint),
        # ("AI内容生成", test_generate_content),
        # ("通义总结 (流式)", test_summarize_tongyi_streaming),
        # ("多轮对话", test_conversation),
        # ("社团介绍生成", test_generate_introduction),
        # ("社团口号生成", test_generate_slogan),
        # ("配置重载", test_reload_config),
        # ("智能申请筛选", test_screen_application),
        # ("社团氛围透视", test_club_atmosphere),
        # ("智能活动策划", test_plan_event),
        # ("智能财务助理 - 对话式记账", test_financial_bookkeeping),
        # ("智能财务助理 - 修改预算", test_update_budget),
        # ("智能财务助理 - 一键生成财务报表", test_generate_financial_report),
        # ("智能财务助理 - 预算超支预警", test_budget_warning),
        # ("社团动态生成", test_generate_activity_post),
        # ("社团推荐", test_club_recommend),
        # ("机器学习数据生成", test_generate_ml_data)
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