import requests
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import os
import sys
import summary
from openai import OpenAI
from fastapi.responses import StreamingResponse

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

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format=config.log_format
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="vLLM Proxy Server",
    description="一个用于转发请求到vLLM服务器的代理服务器",
    version="1.0.0"
)

# 配置CORS
if config.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = config.default_model
    max_tokens: Optional[int] = config.default_max_tokens
    temperature: Optional[float] = config.default_temperature
    top_p: Optional[float] = config.default_top_p
    stream: Optional[bool] = False
    system_prompt: Optional[str] = "You are a helpful assistant."

class ChatResponse(BaseModel):
    response: str
    model: str
    usage: Optional[Dict[str, Any]] = None

class TongyiSummaryRequest(BaseModel):
    text: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1024
    presence_penalty: Optional[float] = 0.0
    top_p: Optional[float] = 1.0

class ContentGenerationRequest(BaseModel):
    content: Optional[str] = None
    style: Optional[str] = None
    expection: Optional[str] = None
    target_people: Optional[str] = None

class SloganGenerationRequest(BaseModel):
    theme: str

class ContentGenerationResponse(BaseModel):
    generated_text: str

# tongyi_chat 函数
api_key_tongyi="sk-354859a6d3ae438fb8ab9b98194f5266"
base_url_tongyi="https://dashscope.aliyuncs.com/compatible-mode/v1"
def tongyi_chat_embedded(messages=None,temperature=0.7,max_tokens=1024,presence_penalty=0.0,top_p=1.0):
    try:        
        client = OpenAI(
            api_key=api_key_tongyi,
            base_url=base_url_tongyi,
        )
        messages_for_api=[
            {"role": "system", "content": "你是一个专业的通知总结专家，请根据通知内容总结，基于通知像人一样总结，更像朋友之间的聊天。"},
            {"role": "user", "content": messages}
        ]
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=messages_for_api,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            top_p=top_p
        )
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                yield{"type": "content", "content": chunk.choices[0].delta.content}
    except Exception as e:
        logger.error(f"通义千问API调用错误: {e}")
        # 可以在这里根据需要抛出更具体的异常或返回错误信息
        # 为了在HTTP响应中捕获，这里不直接 sys.exit(1)
        yield{"type": "error", "content": f"通义千问API调用错误: {e}"}

@app.get("/")
async def root():
    """健康检查接口"""
    return {
        "message": "vLLM代理服务器已启动",
        "status": "running",
        "vllm_api_url": config.vllm_api_url,
        "default_model": config.default_model
    }

@app.get("/health")
async def health_check():
    """详细的健康检查，包括vLLM服务器连接状态"""
    try:
        # 尝试连接vLLM服务器
        health_url = config.vllm_api_url.replace("/v1/chat/completions", "/health")
        response = requests.get(health_url, timeout=5)
        vllm_status = "connected" if response.status_code == 200 else "unavailable"
    except Exception as e:
        logger.warning(f"无法连接到vLLM服务器: {e}")
        vllm_status = "disconnected"
    
    return {
        "proxy_server": "running",
        "vllm_server": vllm_status,
        "vllm_api_url": config.vllm_api_url,
        "server_config": {
            "host": config.server_host,
            "port": config.server_port,
            "default_model": config.default_model
        }
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    接收聊天请求并转发给vLLM服务器
    
    Args:
        request: 包含消息列表和生成参数的请求
        
    Returns:
        ChatResponse: 包含模型响应的响应对象
    """
    try:
        # 构造发送给vLLM的payload
        payload = {
            "model": request.model,
            "messages": [msg.dict() for msg in request.messages],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stream": request.stream
        }
        
        # 如果有系统提示，添加到消息列表开头
        if request.system_prompt:
            payload["messages"].insert(0, {
                "role": "system",
                "content": request.system_prompt
            })
        
        headers = {
            "Content-Type": "application/json"
        }
        
        logger.info(f"转发请求到vLLM服务器: {request.model}")
        logger.info(f"消息数量: {len(request.messages)}")
        
        # 发送请求到vLLM服务器
        # 根据是否流式传输，处理响应
        if request.stream:
            def generate():
                try:
                    response = requests.post(
                        config.vllm_api_url, 
                        headers=headers, 
                        json=payload, 
                        timeout=config.request_timeout,
                        stream=True # 启用流式传输
                    )
                    logger.info(f"vLLM流式响应状态码: {response.status_code}")
                    response.raise_for_status() # 检查HTTP错误

                    for line in response.iter_lines():
                        if line:
                            # Log the raw line for debugging
                            logger.debug(f"接收到vLLM流式原始数据: {line}")
                            # vLLM通常返回SSE格式，直接转发即可
                            # Ensure it's a data line before yielding
                            if line.startswith(b"data:"):
                                yield line + b"\n\n" # 确保每个事件以双换行符结束
                            else:
                                logger.warning(f"接收到非SSE格式行: {line.decode('utf-8')}")

                except requests.exceptions.Timeout:
                    logger.error("请求vLLM服务器超时")
                    yield json.dumps({"error": "请求超时，模型可能需要更长时间来生成回复"}).encode('utf-8') + b"\n\n"
                except requests.exceptions.HTTPError as e: # Catch HTTPError specifically
                    logger.error(f"vLLM服务器返回HTTP错误: {e.response.status_code} - {e.response.text}")
                    yield json.dumps({"error": f"vLLM服务器错误: {e.response.text}"}).encode('utf-8') + b"\n\n"
                except requests.exceptions.ConnectionError as e: # Catch ConnectionError
                    logger.error(f"连接vLLM服务器时发生错误: {e}")
                    yield json.dumps({"error": f"无法连接到vLLM服务器: {str(e)}"}).encode('utf-8') + b"\n\n"
                except requests.exceptions.RequestException as e: # Catch other RequestExceptions
                    error_detail = str(e)
                    if hasattr(e, 'response') and e.response is not None:
                        error_detail += f" - Response Text: {e.response.text}"
                    logger.error(f"请求vLLM服务器时发生未知RequestException: {error_detail}")
                    yield json.dumps({"error": f"请求vLLM服务器时发生未知错误: {str(e)}"}).encode('utf-8') + b"\n\n"
                except Exception as e:
                    logger.error(f"处理请求时发生未知错误: {e}")
                    yield json.dumps({"error": f"服务器内部错误: {str(e)}"}).encode('utf-8') + b"\n\n"

            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            response = requests.post(
                config.vllm_api_url, 
                headers=headers, 
                json=payload, 
                timeout=config.request_timeout
            )
            
            if response.status_code != 200:
                logger.error(f"vLLM服务器返回错误: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"vLLM服务器错误: {response.text}"
                )
            
            result = response.json()
            
            # 检查API响应中是否有错误信息
            if "error" in result:
                logger.error(f"vLLM API返回错误: {result['error']}")
                raise HTTPException(
                    status_code=500,
                    detail=f"vLLM API错误: {result['error']}"
                )
            
            # 提取响应内容
            if result.get("choices") and len(result["choices"]) > 0:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    response_text = choice["message"]["content"]
                    
                    # 构造响应
                    chat_response = ChatResponse(
                        response=response_text,
                        model=request.model,
                        usage=result.get("usage")
                    )
                    
                    logger.info(f"成功生成响应，长度: {len(response_text)}")
                    return chat_response
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="vLLM响应格式错误：缺少message或content字段"
                    )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="vLLM响应中没有有效的choices"
                )
                
    except requests.exceptions.Timeout:
        logger.error("请求vLLM服务器超时")
        raise HTTPException(
            status_code=504,
            detail="请求超时，模型可能需要更长时间来生成回复"
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"请求vLLM服务器时发生错误: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"无法连接到vLLM服务器: {str(e)}"
        )
    except Exception as e:
        logger.error(f"处理请求时发生未知错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@app.post("/simple_chat")
async def simple_chat(prompt: str, model: str = config.default_model, max_tokens: int = config.default_max_tokens):
    """
    简化的聊天接口，只需要提供prompt字符串
    
    Args:
        prompt: 用户输入的提示
        model: 模型名称
        max_tokens: 最大生成token数
        
    Returns:
        包含响应的字典
    """
    # 构造消息列表
    messages = [Message(role="user", content=prompt)]
    
    # 创建请求对象
    request = ChatRequest(
        messages=messages,
        model=model,
        max_tokens=max_tokens
    )
    
    # 调用主聊天接口
    response = await chat(request)
    return {
        "response": response.response,
        "model": response.model
    }

@app.post("/summarize_tongyi")
async def summarize_with_tongyi(req: TongyiSummaryRequest):
    """
    使用通义千问模型总结文本
    
    Args:
        req: 包含要总结文本和可选参数的请求体
        
    Returns:
        包含总结结果的响应对象
    """
    try:
        def generate_summary_stream():
            for chunk in tongyi_chat_embedded(
                messages=req.text,
                temperature=req.temperature,
                max_tokens=req.max_tokens,
                presence_penalty=req.presence_penalty,
                top_p=req.top_p
            ):
                if chunk.get("type") == "content":
                    # 将内容封装为SSE格式的JSON
                    yield f'data: {json.dumps({"summary": chunk.get("content", "")})}\n\n'.encode('utf-8')
                elif chunk.get("type") == "error":
                    logger.error(f"通义千问流式总结错误: {chunk.get('content')}")
                    # 将错误信息封装为SSE格式的JSON
                    yield f'data: {json.dumps({"error": chunk.get("content", "未知错误")})}\n\n'.encode('utf-8')
            # 发送结束标记
            yield b"data: [DONE]\n\n"
        
        return StreamingResponse(generate_summary_stream(), media_type="text/event-stream")

    except Exception as e:
        logger.error(f"调用通义千问总结失败: {e}")
        raise HTTPException(status_code=500, detail=f"通义千问总结失败: {e}")

@app.post("/generate/content", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """
    根据关键词和内容类型，使用AI生成活动宣传或新闻稿。
    
    Args:
        request: 包含关键词、内容类型和语气的请求体。
        
    Returns:
        ContentGenerationResponse: 包含生成的文本。
    """
    try:
        base_prompt = """你是一位文案创作大师，擅长运用多种文体风格进行改写。请根据我提供的原始文案{content}，将其以一种不同的、具有鲜明{style}特征的文体进行改写，并确保每种改写后的内容都达到{expection}的效果。"""
        
        # 格式化Prompt
        full_prompt = base_prompt.format(
            content=request.content,
            style=request.style,
            expection=request.expection
        )
        
        logger.info(f"生成的AI内容Prompt: {full_prompt[:200]}...") # 增加日志长度

        generated_text = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                generated_text += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))

        if not generated_text.strip():
            raise ValueError("AI未返回有效的生成内容。")
            
        return ContentGenerationResponse(generated_text=generated_text.strip())

    except Exception as e:
        logger.error(f"AI内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI内容生成失败: {e}")

@app.post("/generate/introduction", response_model=ContentGenerationResponse)
async def generate_content(request: ContentGenerationRequest):
    """
    根据关键词和内容类型，使用AI生成社团介绍。
    
    Args:
        request: 包含关键词、内容类型和语气的请求体。
        
    Returns:
        ContentGenerationResponse: 包含生成的文本。
    """
    try:
        base_prompt = """你是一位文案创作大师，擅长运用多种文体风格进行改写。请根据我提供的原始文案{content}，将其以一种不同的、具有鲜明{style}特征的文体进行改写，并确保每种改写后的内容都能对{target_people}产生吸引力。"""
        
        # 格式化Prompt
        full_prompt = base_prompt.format(
            content=request.content,
            style=request.style,
            target_people=request.target_people
        )
        
        logger.info(f"生成的AI内容Prompt: {full_prompt[:200]}...") # 增加日志长度

        generated_text = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                generated_text += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))

        if not generated_text.strip():
            raise ValueError("AI未返回有效的生成内容。")
            
        return ContentGenerationResponse(generated_text=generated_text.strip())

    except Exception as e:
        logger.error(f"AI内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI内容生成失败: {e}")

@app.post("/generate/Slogan", response_model=ContentGenerationResponse)
async def generate_content(request: SloganGenerationRequest):
    """
    根据关键词和内容类型，使用AI生成社团口号。
    
    Args:
        request: 包含关键词、内容类型和语气的请求体。
        
    Returns:
        ContentGenerationResponse: 包含生成的文本。
    """
    try:
        base_prompt = """你擅长写宣传口号：1.简短有力；2.突出亮点；3.引发共鸣。 现在你需要根据以下需求写宣传口号：${theme}。"""
        
        # 格式化Prompt
        full_prompt = base_prompt.format(
            theme=request.theme
        )
        
        logger.info(f"生成的AI内容Prompt: {full_prompt[:200]}...") # 增加日志长度

        generated_text = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                generated_text += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))

        if not generated_text.strip():
            raise ValueError("AI未返回有效的生成内容。")
            
        return ContentGenerationResponse(generated_text=generated_text.strip())

    except Exception as e:
        logger.error(f"AI内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI内容生成失败: {e}")

@app.get("/models")
async def list_models():
    """
    获取可用的模型列表（从vLLM服务器）
    """
    try:
        models_url = config.vllm_api_url.replace("/v1/chat/completions", "/v1/models")
        response = requests.get(models_url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.warning(f"无法获取模型列表: {response.status_code}")
            return {
                "data": [
                    {
                        "id": config.default_model,
                        "object": "model",
                        "created": 0,
                        "owned_by": "vllm"
                    }
                ]
            }
    except Exception as e:
        logger.warning(f"获取模型列表时发生错误: {e}")
        return {
            "data": [
                {
                    "id": config.default_model,
                    "object": "model",
                    "created": 0,
                    "owned_by": "vllm"
                }
            ]
        }

@app.get("/config")
async def get_config():
    """
    获取当前服务器配置（不包含敏感信息）
    """
    return {
        "server": {
            "host": config.server_host,
            "port": config.server_port
        },
        "vllm": {
            "api_url": config.vllm_api_url,
            "default_model": config.default_model
        },
        "request": {
            "default_max_tokens": config.default_max_tokens,
            "default_temperature": config.default_temperature,
            "default_top_p": config.default_top_p,
            "timeout": config.request_timeout
        },
        "logging": {
            "level": config.log_level
        },
        "security": {
            "enable_cors": config.enable_cors
        }
    }

if __name__ == "__main__":
    print(f"启动vLLM代理服务器...")
    print(f"服务器地址: http://{config.server_host}:{config.server_port}")
    print(f"vLLM API地址: {config.vllm_api_url}")
    print(f"默认模型: {config.default_model}")
    print(f"健康检查: http://{config.server_host}:{config.server_port}/health")
    print(f"聊天接口: http://{config.server_host}:{config.server_port}/chat")
    print(f"简化接口: http://{config.server_host}:{config.server_port}/simple_chat")
    print(f"通义总结接口: http://{config.server_host}:{config.server_port}/summarize_tongyi")
    print(f"生成内容接口: http://{config.server_host}:{config.server_port}/generate/content")
    print(f"社团介绍接口: http://{config.server_host}:{config.server_port}/generate/introduction")
    print(f"社团口号接口: http://{config.server_host}:{config.server_port}/generate/Slogan")
    print(f"模型列表: http://{config.server_host}:{config.server_port}/models")
    print(f"配置信息: http://{config.server_host}:{config.server_port}/config")
    
    uvicorn.run(
        app,
        host=config.server_host,
        port=config.server_port,
        log_level=config.log_level.lower()
    ) 