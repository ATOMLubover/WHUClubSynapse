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
import time

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
    stream: Optional[bool] = True
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

# 新增申请筛选助手请求和响应模型
class ApplicationScreeningRequest(BaseModel):
    applicant_data: Dict[str, Any] # 申请者个人资料，如姓名、专业、技能等
    application_reason: str       # 申请理由
    required_conditions: List[str] # 社团标签
    club_name: str #社团名称

class ApplicationScreeningResponse(BaseModel):
    summary: str    # AI生成的申请摘要
    suggestion: str # AI生成的建议

# 新增社团氛围透视镜请求和响应模型
class ClubAtmosphereRequest(BaseModel):
    communication_content: str # 社团内部的交流内容，如论坛帖子、聊天记录摘要等

class ClubAtmosphereResponse(BaseModel):
    atmosphere_tags: List[str] # AI生成的氛围标签列表
    culture_summary: str       # AI生成的文化摘要

# 新增活动策划请求和响应模型
class EventPlanningRequest(BaseModel):
    event_idea: str # 用户输入的活动想法，如"我们想为50人办一场户外烧烤"

class EventPlanningResponse(BaseModel):
    checklist: List[str]      # 待办事项清单
    budget_estimate: str      # 预算智能估算
    risk_assessment: str      # 风险评估与预案
    creative_ideas: List[str] # 创意点子推荐

# 新增智能财务助理请求和响应模型
class FinancialEntry(BaseModel):
    item: str # 购买的物品或服务
    amount: float # 金额
    category: Optional[str] = "未分类" # 支出类别，如餐饮、交通、物资等
    payer: Optional[str] = None # 经手人/报销人
    date: Optional[str] = None # 发生日期，默认为空，AI可以尝试解析
    remark: Optional[str] = None # 备注信息

class FinancialBookkeepingRequest(BaseModel):
    natural_language_input: str # 用户输入的自然语言记账文本
    club_name: str # 社团名称

class FinancialBookkeepingResponse(BaseModel):
    parsed_entries: List[FinancialEntry] # AI解析出的财务条目列表
    confirmation_message: str # AI生成的确认信息或提示
    original_input: str # 原始输入，方便调试

# 新增财务报表生成请求和响应模型
class FinancialReportRequest(BaseModel):
    club_name: str # 社团名称

class FinancialReportResponse(BaseModel):
    report_summary: str # 财务报表总结
    expense_breakdown: Dict[str, float] # 支出分类汇总
    income_breakdown: Dict[str, float] # 收入分类汇总 (如果包含收入概念)

# 新增预算超支预警请求和响应模型
class BudgetWarningRequest(BaseModel):
    current_spending: float # 当前已支出金额 (本次请求的即时支出，不持久化)
    budget_limit: Optional[float] = None # 本次请求传入的预算限制，如果提供则覆盖社团存储的预算限制
    description: Optional[str] = None # 可选的描述信息，例如活动名称
    club_name: str # 社团名称

class BudgetWarningResponse(BaseModel):
    warning_message: str # 预警信息
    is_over_budget: bool # 是否超预算
    percentage_used: float # 预算使用百分比
    club_budget_limit: Optional[float] = None # 社团存储的预算上限
    club_budget_description: Optional[str] = None # 社团存储的预算描述

# 新增修改预算请求模型
class UpdateBudgetRequest(BaseModel):
    club_name: str # 社团名称
    new_budget_limit: float # 新的预算总额
    budget_description: Optional[str] = None # 预算描述
    
class UpdateBudgetResponse(BaseModel):
    message: str
    club_name: str
    new_budget_limit: float
    budget_description: Optional[str] = None

# 新增外部API的Pydantic模型
class ClubListResponseItem(BaseModel):
    club_id: int
    club_name: str
    category: int
    tags: str # 原始是字符串，后续需要反序列化
    logo_url: str
    desc: str
    created_at: str
    member_count: int

class MemberInfo(BaseModel):
    member_id: int
    user_id: int
    club_id: int
    role_in_club: str
    joined_at: str
    last_active: str

class PostInfo(BaseModel):
    post_id: int
    club_id: int
    author_id: int
    title: str
    comment_count: int
    created_at: str

class ClubDetailResponse(BaseModel):
    club_id: int
    club_name: str
    category: int
    tags: str # 原始是字符串，后续需要反序列化
    logo_url: str
    desc: str
    created_at: str
    member_count: int
    members: List[MemberInfo]
    posts: List[PostInfo]

class ClubInfo(BaseModel):
    club_name: str
    description: str
    tags: List[str]
    recommend_reason: str

class Club_Recommend_Request(BaseModel):
    User_name: str
    User_description: str
    User_tags: List[str]
    User_major: str

class Club_Recommend_Response(BaseModel):
    Summary_text: str
    Recommend_club_list: List[ClubInfo]

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

# 全局财务数据存储路径
FINANCIAL_DATA_FILE = os.path.join(current_dir, config.financial_data_file)

def load_financial_data() -> Dict[str, Any]:
    """从JSON文件加载所有社团的财务数据"""
    if not os.path.exists(FINANCIAL_DATA_FILE):
        return {} # 如果文件不存在，返回一个空字典
    try:
        with open(FINANCIAL_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict): # 确保加载的是字典
                logger.error(f"财务数据文件格式错误，应为字典，但加载到: {type(data)}")
                os.rename(FINANCIAL_DATA_FILE, f"{FINANCIAL_DATA_FILE}.bak_{int(time.time())}")
                logger.warning(f"已备份损坏的财务数据文件到 {FINANCIAL_DATA_FILE}.bak_{int(time.time())}")
                return {}
            return data
    except json.JSONDecodeError as e:
        logger.error(f"加载财务数据文件时JSON解析错误: {e}")
        # 备份损坏的文件并返回空字典，避免影响服务
        os.rename(FINANCIAL_DATA_FILE, f"{FINANCIAL_DATA_FILE}.bak_{int(time.time())}")
        logger.warning(f"已备份损坏的财务数据文件到 {FINANCIAL_DATA_FILE}.bak_{int(time.time())}")
        return {}
    except Exception as e:
        logger.error(f"加载财务数据文件失败: {e}")
        return {}

def save_financial_data(data: Dict[str, Any]):
    """将所有社团的财务数据保存到JSON文件"""
    try:
        with open(FINANCIAL_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"保存财务数据文件失败: {e}")

# 全局社团信息存储路径
CLUB_INFORMATION_FILE = os.path.join(current_dir, config.club_information_file) if hasattr(config, 'club_information_file') else os.path.join(current_dir, 'Club_information.json')

def load_club_information() -> Dict[str, Any]:
    """从JSON文件加载所有社团的信息"""
    if not os.path.exists(CLUB_INFORMATION_FILE):
        return {} # 如果文件不存在，返回一个空字典
    try:
        with open(CLUB_INFORMATION_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict): # 确保加载的是字典
                logger.error(f"社团信息文件格式错误，应为字典，但加载到: {type(data)}")
                os.rename(CLUB_INFORMATION_FILE, f"{CLUB_INFORMATION_FILE}.bak_{int(time.time())}")
                logger.warning(f"已备份损坏的社团信息文件到 {CLUB_INFORMATION_FILE}.bak_{int(time.time())}")
                return {}
            return data
    except json.JSONDecodeError as e:
        logger.error(f"加载社团信息文件时JSON解析错误: {e}")
        os.rename(CLUB_INFORMATION_FILE, f"{CLUB_INFORMATION_FILE}.bak_{int(time.time())}")
        logger.warning(f"已备份损坏的社团信息文件到 {CLUB_INFORMATION_FILE}.bak_{int(time.time())}")
        return {}
    except Exception as e:
        logger.error(f"加载社团信息文件失败: {e}")
        return {}

def save_club_information(data: Dict[str, Any]):
    """将所有社团的信息保存到JSON文件"""
    try:
        with open(CLUB_INFORMATION_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"保存社团信息文件失败: {e}")

async def fetch_club_list(offset: int = 0, num: int = 100) -> List[ClubListResponseItem]:
    """从远程API获取社团列表"""
    try:
        if not hasattr(config, 'external_api') or not hasattr(config.external_api, 'base_url'):
            logger.error("config.json中未配置external_api.base_url")
            raise HTTPException(status_code=500, detail="外部API基础URL未配置")
        
        url = f"{config.external_api.base_url}/api/club/list?offset={offset}&num={num}"
        logger.info(f"正在从 {url} 获取社团列表")
        response = requests.get(url, timeout=config.request_timeout)
        response.raise_for_status() # 检查HTTP错误
        
        club_list_data = response.json()
        clubs = [ClubListResponseItem(**item) for item in club_list_data]
        logger.info(f"成功获取 {len(clubs)} 个社团的列表")
        return clubs
    except requests.exceptions.Timeout:
        logger.error("获取社团列表超时")
        raise HTTPException(status_code=504, detail="获取社团列表超时")
    except requests.exceptions.RequestException as e:
        logger.error(f"获取社团列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取社团列表失败: {e}")
    except Exception as e:
        logger.error(f"处理社团列表时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")

async def fetch_club_details(club_id: int, post_num: int = 5) -> ClubDetailResponse:
    """从远程API获取单个社团的详细信息"""
    try:
        if not hasattr(config, 'external_api') or not hasattr(config.external_api, 'base_url'):
            logger.error("config.json中未配置external_api.base_url")
            raise HTTPException(status_code=500, detail="外部API基础URL未配置")

        url = f"{config.external_api.base_url}/api/club/{club_id}/info?post_num={post_num}"
        logger.info(f"正在从 {url} 获取社团详情 (ID: {club_id})")
        response = requests.get(url, timeout=config.request_timeout)
        response.raise_for_status() # 检查HTTP错误

        club_detail_data = response.json()
        club_detail = ClubDetailResponse(**club_detail_data)
        logger.info(f"成功获取社团 (ID: {club_id}) 的详情")
        return club_detail
    except requests.exceptions.Timeout:
        logger.error(f"获取社团 (ID: {club_id}) 详情超时")
        raise HTTPException(status_code=504, detail=f"获取社团 (ID: {club_id}) 详情超时")
    except requests.exceptions.RequestException as e:
        logger.error(f"获取社团 (ID: {club_id}) 详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取社团 (ID: {club_id}) 详情失败: {e}")
    except Exception as e:
        logger.error(f"处理社团 (ID: {club_id}) 详情时发生未知错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")

async def update_club_information():
    """获取所有社团列表和详情，并保存到本地JSON文件"""
    try:
        all_clubs_data = {}
        offset = 0
        num = 100
        while True:
            club_list = await fetch_club_list(offset=offset, num=num)
            if not club_list:
                break
            
            for club_item in club_list:
                try:
                    club_detail = await fetch_club_details(club_id=club_item.club_id)
                    # 反序列化tags字段
                    try:
                        club_detail.tags = json.loads(club_detail.tags)
                    except json.JSONDecodeError:
                        logger.warning(f"社团 {club_detail.club_name} (ID: {club_detail.club_id}) 的tags字段无法解析为JSON: {club_detail.tags}")
                        club_detail.tags = [club_detail.tags] # 如果解析失败，将其作为单个标签列表

                    # 将ClubDetailResponse对象转换为字典并存储
                    all_clubs_data[str(club_detail.club_id)] = club_detail.dict()
                except HTTPException as e:
                    logger.error(f"获取社团 {club_item.club_name} (ID: {club_item.club_id}) 详情失败: {e.detail}")
                except Exception as e:
                    logger.error(f"处理社团 {club_item.club_name} (ID: {club_item.club_id}) 详情时发生未知错误: {e}")
            
            offset += num
            if len(club_list) < num: # 如果返回的列表数量小于请求的数量，说明已经到末尾
                break
        
        save_club_information(all_clubs_data)
        logger.info(f"成功更新了 {len(all_clubs_data)} 个社团的信息到 {CLUB_INFORMATION_FILE}")
        return {"message": f"成功更新了 {len(all_clubs_data)} 个社团的信息", "status": "success"}
    except Exception as e:
        logger.error(f"更新社团信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新社团信息失败: {e}")

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
                yield ("data: " + json.dumps({"summary": chunk.get("content", "")}) + "\n\n").encode('utf-8')
            elif chunk.get("type") == "error":
                logger.error("通义千问流式总结错误: {}".format(chunk.get('content')))
                # 将错误信息封装为SSE格式的JSON
                yield ("data: " + json.dumps({"error": chunk.get("content", "未知错误")}) + "\n\n").encode('utf-8')
        # 发送结束标记
        yield b"data: [DONE]\n\n"
    
    return StreamingResponse(generate_summary_stream(), media_type="text/event-stream")

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

@app.get("/reload_config")
async def reload_config_endpoint():
    """重载配置文件"""
    try:
        config.reload()
        logger.info("配置文件已成功重载")
        return {"message": "配置文件已成功重载", "status": "success"}
    except Exception as e:
        logger.error(f"重载配置文件失败: {e}")
        raise HTTPException(status_code=500, detail=f"重载配置文件失败: {e}")

@app.post("/screen_application", response_model=ApplicationScreeningResponse)
async def screen_application(request: ApplicationScreeningRequest):
    """
    智能申请筛选助手，自动分析申请理由和个人资料，生成摘要和建议。
    
    Args:
        request: 包含申请者资料、申请理由和社团所需条件的请求体。
        
    Returns:
        ApplicationScreeningResponse: 包含AI生成的摘要和建议。
    """
    try:
        # 构建详细的LLM提示
        prompt_template = """
你是一个智能社团申请筛选助手，你的任务是根据申请者的资料和社团的招新要求，对申请进行评估，并生成简洁的摘要和明确的建议。

请按照以下JSON格式返回结果：
{{
  "summary": "[AI生成的申请摘要]",
  "suggestion": "[AI生成的建议]"
}}

--- 申请信息 ---
申请者资料: {applicant_data}
申请理由: {application_reason}
--- 社团名称 ---
{club_name}

--- 社团特质 ---
{required_conditions_str}

请开始评估并生成摘要和建议。
"""
        
        required_conditions_str = "\n".join([f"- {cond}" for cond in request.required_conditions])

        full_prompt = prompt_template.format(
            applicant_data=json.dumps(request.applicant_data, ensure_ascii=False, indent=2),
            application_reason=request.application_reason,
            required_conditions_str=required_conditions_str,
            club_name=request.club_name
        )
        
        logger.info(f"AI申请筛选Prompt: {full_prompt[:200]}...") # 增加日志长度

        llm_response_content = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                llm_response_content += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))
        
        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        # 尝试解析LLM的JSON响应，先移除可能的markdown代码块
        json_string = llm_response_content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[len("```json"): -len("```")].strip()
        
        try:
            parsed_response = json.loads(json_string)
            summary = parsed_response.get("summary", "")
            suggestion = parsed_response.get("suggestion", "")
            
            if not summary or not suggestion:
                raise ValueError("AI返回的JSON格式不完整，缺少summary或suggestion字段。")

            return ApplicationScreeningResponse(summary=summary.strip(), suggestion=suggestion.strip())
        except json.JSONDecodeError:
            logger.error(f"AI响应不是有效的JSON: {llm_response_content}")
            raise ValueError(f"AI返回的响应格式错误，无法解析为JSON: {llm_response_content[:100]}...")
            
    except Exception as e:
        logger.error(f"AI申请筛选失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI申请筛选失败: {e}")

@app.post("/club_atmosphere", response_model=ClubAtmosphereResponse)
async def club_atmosphere(request: ClubAtmosphereRequest):
    """
    社团"氛围"透视镜，对社团内部交流内容进行情感分析和主题建模，生成氛围标签和文化摘要。
    
    Args:
        request: 包含社团内部交流内容的请求体。
        
    Returns:
        ClubAtmosphereResponse: 包含AI生成的氛围标签和文化摘要。
    """
    try:
        # 构建LLM提示
        prompt_template = """
你是一个社团氛围透视镜AI，你的任务是根据社团内部的交流内容，分析其情感和主题，并生成社团的"氛围标签"和一段"文化摘要"。
在保护隐私的前提下，请不要提及具体的人名，只关注整体氛围和趋势。

请按照以下JSON格式返回结果：
{{
  "atmosphere_tags": ["标签1", "标签2", "标签3"],
  "culture_summary": "[AI生成的文化摘要]"
}}

--- 社团交流内容 ---
{communication_content}

请开始分析并生成氛围标签和文化摘要。
"""
        
        full_prompt = prompt_template.format(
            communication_content=request.communication_content
        )
        
        logger.info(f"AI社团氛围透视Prompt: {full_prompt[:200]}...") # 增加日志长度

        llm_response_content = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                llm_response_content += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))
        
        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        # 尝试解析LLM的JSON响应，先移除可能的markdown代码块
        json_string = llm_response_content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[len("```json"): -len("```")].strip()
        
        try:
            parsed_response = json.loads(json_string)
            atmosphere_tags = parsed_response.get("atmosphere_tags", [])
            culture_summary = parsed_response.get("culture_summary", "")
            
            if not isinstance(atmosphere_tags, list) or not all(isinstance(tag, str) for tag in atmosphere_tags):
                raise ValueError("AI返回的atmosphere_tags格式不正确，应为字符串列表。")
            if not culture_summary:
                raise ValueError("AI返回的JSON格式不完整，缺少culture_summary字段。")

            return ClubAtmosphereResponse(atmosphere_tags=atmosphere_tags, culture_summary=culture_summary.strip())
        except json.JSONDecodeError:
            logger.error(f"AI响应不是有效的JSON: {llm_response_content}")
            raise ValueError(f"AI返回的响应格式错误，无法解析为JSON: {llm_response_content[:100]}...")
            
    except Exception as e:
        logger.error(f"AI社团氛围透视失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI社团氛围透视失败: {e}")

@app.post("/plan_event", response_model=EventPlanningResponse)
async def plan_event(request: EventPlanningRequest):
    """
    智能活动策划参谋，根据用户输入的活动想法生成完整的策划框架。
    
    Args:
        request: 包含活动想法的请求体。
        
    Returns:
        EventPlanningResponse: 包含AI生成的策划清单、预算估算、风险评估和创意点子。
    """
    try:
        # 构建LLM提示
        prompt_template = """
你是一个智能活动策划参谋AI，你的任务是根据用户提供的活动想法，生成一份详尽的策划框架。
这份框架应包括待办事项清单、预算智能估算、风险评估与预案，以及创意点子推荐。

请按照以下JSON格式返回结果：
{{
  "checklist": [
    "[待办事项1]",
    "[待办事项2]",
    "..."
  ],
  "budget_estimate": "[预算估算描述]",
  "risk_assessment": "[风险评估与预案描述]",
  "creative_ideas": [
    "[创意点子1]",
    "[创意点子2]",
    "..."
  ]
}}

--- 活动想法 ---
{event_idea}

请开始生成活动策划框架。
"""
        
        full_prompt = prompt_template.format(
            event_idea=request.event_idea
        )
        
        logger.info(f"AI活动策划Prompt: {full_prompt[:200]}...")

        llm_response_content = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                llm_response_content += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))
        
        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        # 尝试解析LLM的JSON响应，先移除可能的markdown代码块
        json_string = llm_response_content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[len("```json"): -len("```")].strip()
        
        try:
            parsed_response = json.loads(json_string)
            checklist = parsed_response.get("checklist", [])
            budget_estimate = parsed_response.get("budget_estimate", "")
            risk_assessment = parsed_response.get("risk_assessment", "")
            creative_ideas = parsed_response.get("creative_ideas", [])
            
            if not isinstance(checklist, list) or not all(isinstance(item, str) for item in checklist):
                raise ValueError("AI返回的checklist格式不正确，应为字符串列表。")
            if not budget_estimate or not risk_assessment:
                raise ValueError("AI返回的JSON格式不完整，缺少budget_estimate或risk_assessment字段。")
            if not isinstance(creative_ideas, list) or not all(isinstance(item, str) for item in creative_ideas):
                raise ValueError("AI返回的creative_ideas格式不正确，应为字符串列表。")

            return EventPlanningResponse(
                checklist=checklist,
                budget_estimate=budget_estimate.strip(),
                risk_assessment=risk_assessment.strip(),
                creative_ideas=creative_ideas
            )
        except json.JSONDecodeError:
            logger.error(f"AI响应不是有效的JSON: {llm_response_content}")
            raise ValueError(f"AI返回的响应格式错误，无法解析为JSON: {llm_response_content[:100]}...")
            
    except Exception as e:
        logger.error(f"AI活动策划失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI活动策划失败: {e}")

@app.post("/financial_bookkeeping", response_model=FinancialBookkeepingResponse)
async def financial_bookkeeping(request: FinancialBookkeepingRequest):
    """
    智能财务助理 - 对话式记账接口。
    根据自然语言输入，AI自动解析并记录财务条目。
    
    Args:
        request: 包含自然语言记账文本和社团名称的请求体。
        
    Returns:
        FinancialBookkeepingResponse: 包含AI解析出的财务条目和确认信息。
    """
    try:
        # 构造发送给vLLM的payload
        prompt_template = """
你是一个智能财务助理，你的任务是根据用户输入的自然语言描述，解析出财务支出或收入的详细信息，并生成结构化的记账条目和友好的确认信息。

请优先解析以下信息：
- **物品/服务 (item)**: 具体购买或涉及的物品或服务。
- **金额 (amount)**: 具体的金额，应为数字。
- **类别 (category)**: 支出或收入的类别（如餐饮、交通、物资、办公、活动、报销等）。如果无法明确分类，请使用"未分类"。
- **经手人/报销人 (payer)**: 涉及的经手人或需要报销的人名。
- **日期 (date)**: 如果描述中包含日期信息，请解析出来。
- **备注 (remark)**: 任何其他相关信息。

请按照以下JSON格式返回结果：
{{
  "parsed_entries": [
    {{
      "item": "[物品/服务描述]",
      "amount": [金额，浮点数],
      "category": "[类别，默认为"未分类"]",
      "payer": "[经手人/报销人，如果没有则为null]",
      "date": "[日期，例如"今天"、"昨天"、"2023-10-26"，如果没有则为null]",
      "remark": "[备注信息，如果没有则为null]"
    }},
    // 如果有多个条目，可以继续添加
  ],
  "confirmation_message": "[AI生成的确认信息或总结，例如"好的，已为您记录…"、"本次消费明细如下:…"。用友好的语气，总结记账内容，以便用户确认。]"
}}

--- 用户输入 ---
{natural_language_input}

请开始解析并生成财务条目和确认信息。
"""
        
        full_prompt = prompt_template.format(
            natural_language_input=request.natural_language_input
        )
        
        logger.info(f"AI财务记账Prompt: {full_prompt[:200]}...")

        llm_response_content = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                llm_response_content += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))
        
        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        # 尝试解析LLM的JSON响应，先移除可能的markdown代码块
        json_string = llm_response_content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[len("```json"): -len("```")].strip()
        
        try:
            parsed_response = json.loads(json_string)
            parsed_entries_data = parsed_response.get("parsed_entries", [])
            confirmation_message = parsed_response.get("confirmation_message", "")

            # 验证 parsed_entries_data 中的每个条目是否符合 FinancialEntry 模型
            parsed_entries = []
            for entry_data in parsed_entries_data:
                try:
                    entry = FinancialEntry(**entry_data)
                    parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"解析单个财务条目时出错: {entry_data}, 错误: {e}")
                    # 如果单个条目解析失败，可以跳过或记录错误，这里选择跳过不完整的条目
            
            if not confirmation_message:
                raise ValueError("AI返回的JSON格式不完整，缺少confirmation_message字段。")

            # 将新解析的条目保存到文件，按社团名称存储
            all_clubs_data = load_financial_data()
            if request.club_name not in all_clubs_data:
                all_clubs_data[request.club_name] = {"entries": [], "budget": {}} # Initialize with empty budget

            for entry in parsed_entries:
                all_clubs_data[request.club_name]["entries"].append(entry.dict())
            save_financial_data(all_clubs_data)

            return FinancialBookkeepingResponse(
                parsed_entries=parsed_entries,
                confirmation_message=confirmation_message.strip(),
                original_input=request.natural_language_input
            )
        except json.JSONDecodeError:
            logger.error(f"AI响应不是有效的JSON: {llm_response_content}")
            raise ValueError(f"AI返回的响应格式错误，无法解析为JSON: {llm_response_content[:100]}...")
            
    except Exception as e:
        logger.error(f"AI财务记账失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI财务记账失败: {e}")

@app.post("/generate_financial_report", response_model=FinancialReportResponse)
async def generate_financial_report(request: FinancialReportRequest):
    """
    智能财务助理 - 一键生成财务报表。
    根据提供的社团名称，AI自动汇总收支并生成清晰的财务报表摘要。
    
    Args:
        request: 包含社团名称的请求体。
        
    Returns:
        FinancialReportResponse: 包含AI生成的报表总结、支出分类和收入分类。
    """
    try:
        all_clubs_data = load_financial_data()
        club_data = all_clubs_data.get(request.club_name)

        if not club_data or not club_data.get("entries"): # Check if club_data exists and has entries
            raise HTTPException(
                status_code=404,
                detail=f"未找到社团 '{request.club_name}' 的财务数据或账目为空。"
            )

        entries_to_report = [FinancialEntry(**entry_data) for entry_data in club_data["entries"]]

        entries_str = "\n".join([
            f"- {entry.date if entry.date else '日期未知'}: {entry.item} - {entry.amount:.2f}元 ({entry.category}) - 经手人: {entry.payer if entry.payer else '未知'}"
            for entry in entries_to_report
        ])

        prompt_template = """
你是一个智能财务报表生成助手，你的任务是根据用户提供的财务流水，生成一份清晰、专业的财务报表总结，并详细列出各项支出和收入的分类汇总。请注意，这里主要是支出，如果出现收入字样可以进行分类。

请**直接**按照以下JSON格式返回结果，**不要包含任何Markdown代码块或其他文本**：
{{
  "report_summary": "[AI生成的财务报表总结，包括总支出、可能存在的总收入、主要支出类别等，用友好的语言描述。]",
  "expense_breakdown": {{
    "[类别1]": [金额],
    "[类别2]": [金额],
    "...",
    "总支出": [总支出金额]
  }},
  "income_breakdown": {{
    "[收入类别1]": [金额],
    "...",
    "总收入": [总收入金额]
  }}
}}

--- 财务流水 ---
{financial_entries_str}

请开始分析并生成财务报表。
"""

        full_prompt = prompt_template.format(
            financial_entries_str=entries_str
        )

        logger.info(f"AI财务报表Prompt: {full_prompt[:200]}...")

        llm_response_content = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                llm_response_content += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))

        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        # 尝试解析LLM的JSON响应，先移除可能的markdown代码块
        json_string = llm_response_content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[len("```json"): -len("```")].strip()

        try:
            parsed_response = json.loads(json_string)
            report_summary = parsed_response.get("report_summary", "")
            expense_breakdown = parsed_response.get("expense_breakdown", {})
            income_breakdown = parsed_response.get("income_breakdown", {})

            if not report_summary or not isinstance(expense_breakdown, dict) or not isinstance(income_breakdown, dict):
                raise ValueError("AI返回的JSON格式不完整或字段类型不正确。")

            return FinancialReportResponse(
                report_summary=report_summary.strip(),
                expense_breakdown=expense_breakdown,
                income_breakdown=income_breakdown
            )
        except json.JSONDecodeError:
            logger.error(f"AI响应不是有效的JSON: {llm_response_content}")
            raise ValueError(f"AI返回的响应格式错误，无法解析为JSON: {llm_response_content[:100]}...")
            
    except HTTPException as http_exc: # Re-raise HTTPException directly
        raise http_exc
    except Exception as e:
        logger.error(f"AI财务报表生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI财务报表生成失败: {e}")

@app.post("/budget_warning", response_model=BudgetWarningResponse)
async def budget_warning(request: BudgetWarningRequest):
    """
    智能财务助理 - 预算超支预警。
    根据当前支出和社团存储的预算总额（或本次请求传入的临时预算），AI判断是否超支并生成预警信息。
    
    Args:
        request: 包含当前支出、可选的临时预算总额、描述和社团名称的请求体。
        
    Returns:
        BudgetWarningResponse: 包含预警信息、是否超预算标志和预算使用百分比。
    """
    try:
        all_clubs_data = load_financial_data()
        club_data = all_clubs_data.get(request.club_name)

        club_budget_limit = None
        club_budget_description = None

        if club_data and club_data.get("budget"):
            club_budget_limit = club_data["budget"].get("limit")
            club_budget_description = club_data["budget"].get("description")

        # Determine the budget limit to use for warning
        effective_budget_limit = request.budget_limit if request.budget_limit is not None else club_budget_limit

        if effective_budget_limit is None:
            raise HTTPException(
                status_code=400,
                detail=f"社团 '{request.club_name}' 未设置预算，或请求中未提供预算限制。请先设置预算。"
            )
        if effective_budget_limit <= 0:
            raise HTTPException(
                status_code=400,
                detail="预算限制必须大于0。"
            )

        percentage_used = (request.current_spending / effective_budget_limit) * 100
        is_over_budget = request.current_spending > effective_budget_limit

        prompt_template = """
你是一个预算管理助手，你的任务是根据当前的支出和预算限额，判断是否超支，并生成一个友好的预警信息。如果用户提供了描述信息，请在预警信息中提及。

请按照以下JSON格式返回结果：
{{
  "warning_message": "[AI生成的预警信息，例如"您好，[活动名称]的支出已接近预算上限，请注意控制。"或"恭喜，[活动名称]的支出仍在预算范围内！"]]",
  "is_over_budget": [true/false],
  "percentage_used": [预算使用百分比，浮点数，例如95.5]
}}

--- 预算信息 ---
当前已支出金额: {current_spending:.2f}元
预算总额: {budget_limit:.2f}元
预算使用百分比: {percentage_used:.2f}%
是否超预算: {is_over_budget}
社团名称: {club_name}
{description_str}

请开始生成预警信息。
"""

        description_str = f"描述: {request.description}" if request.description else ""

        full_prompt = prompt_template.format(
            current_spending=request.current_spending,
            budget_limit=effective_budget_limit,
            percentage_used=percentage_used,
            is_over_budget=is_over_budget,
            club_name=request.club_name,
            description_str=description_str
        )

        logger.info(f"AI预算预警Prompt: {full_prompt[:200]}...")

        llm_response_content = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                llm_response_content += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))

        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        json_string = llm_response_content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[len("```json"): -len("```")].strip()

        try:
            parsed_response = json.loads(json_string)
            warning_message = parsed_response.get("warning_message", "")
            is_over_budget_from_ai = parsed_response.get("is_over_budget", False)
            percentage_used_from_ai = parsed_response.get("percentage_used", 0.0)

            if not warning_message or not isinstance(is_over_budget_from_ai, bool) or not isinstance(percentage_used_from_ai, (float, int)):
                raise ValueError("AI返回的JSON格式不完整或字段类型不正确。")

            return BudgetWarningResponse(
                warning_message=warning_message.strip(),
                is_over_budget=is_over_budget_from_ai,
                percentage_used=percentage_used_from_ai,
                club_budget_limit=club_budget_limit,
                club_budget_description=club_budget_description
            )
        except json.JSONDecodeError:
            logger.error(f"AI响应不是有效的JSON: {llm_response_content}")
            raise ValueError(f"AI返回的响应格式错误，无法解析为JSON: {llm_response_content[:100]}...")

    except HTTPException as http_exc: # Re-raise HTTPException directly
        raise http_exc
    except Exception as e:
        logger.error(f"AI预算预警失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI预算预警失败: {e}")

@app.post("/update_budget", response_model=UpdateBudgetResponse)
async def update_budget(request: UpdateBudgetRequest):
    """
    智能财务助理 - 修改预算。
    根据新的预算总额和描述，更新社团的预算限制。
    
    Args:
        request: 包含社团名称、新的预算总额和预算描述的请求体。
        
    Returns:
        UpdateBudgetResponse: 包含更新结果的消息。
    """
    try:
        all_clubs_data = load_financial_data()

        if request.club_name not in all_clubs_data:
            # If club does not exist, initialize it with empty entries and budget
            all_clubs_data[request.club_name] = {"entries": [], "budget": {}} # Initialize with empty budget

        # Update the budget for the specific club
        all_clubs_data[request.club_name]["budget"] = {
            "limit": request.new_budget_limit,
            "description": request.budget_description
        }

        save_financial_data(all_clubs_data)

        return UpdateBudgetResponse(
            message=f"{request.club_name} 的预算已成功更新",
            club_name=request.club_name,
            new_budget_limit=request.new_budget_limit,
            budget_description=request.budget_description
        )

    except Exception as e:
        logger.error(f"AI修改预算失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI修改预算失败: {e}")

LOCAL_SYNCED_DATA_FILE = os.path.join(current_dir, '..', 'data', 'local_synced_data.jsonl')

def load_local_synced_data() -> Dict[str, Any]:
    """
    从 local_synced_data.jsonl 文件加载社团和帖子信息。
    将帖子归类到对应的社团下。
    """
    clubs_data = {}
    
    if not os.path.exists(LOCAL_SYNCED_DATA_FILE):
        logger.warning(f"本地同步数据文件不存在: {LOCAL_SYNCED_DATA_FILE}")
        return {}

    try:
        with open(LOCAL_SYNCED_DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    doc_id = entry.get("id", "")
                    metadata = entry.get("metadata", {})
                    document_content = entry.get("document", "")

                    if doc_id.startswith("dynamic::club_id::"):
                        club_id = doc_id.replace("dynamic::club_id::", "")
                        if club_id not in clubs_data:
                            clubs_data[club_id] = {
                                "club_name": metadata.get("name", f"未知社团 {club_id}"),
                                "description": metadata.get("description", document_content),
                                "tags": [],
                                "posts": []
                            }
                        # Parse tags, which might be a JSON string
                        raw_tags = metadata.get("tags", "[]")
                        try:
                            parsed_tags = json.loads(raw_tags)
                            if isinstance(parsed_tags, list) and all(isinstance(t, str) for t in parsed_tags):
                                clubs_data[club_id]["tags"] = parsed_tags
                            else:
                                clubs_data[club_id]["tags"] = [raw_tags] # Fallback if not a proper list
                        except json.JSONDecodeError:
                            clubs_data[club_id]["tags"] = [raw_tags] # Treat as single tag if not JSON array

                        # Update description if document_content is more relevant
                        if document_content and document_content != "some description":
                            clubs_data[club_id]["description"] = document_content

                    elif doc_id.startswith("dynamic::post_id::"):
                        post_club_id = str(metadata.get("club_id")) # Ensure it's a string to match club_id keys
                        if post_club_id in clubs_data:
                            post_info = {
                                "id": doc_id,
                                "document": document_content,
                                "title": metadata.get("title", ""),
                                "author_id": metadata.get("author_id"),
                                "is_pinned": metadata.get("is_pinned")
                            }
                            clubs_data[post_club_id]["posts"].append(post_info)
                        else:
                            logger.warning(f"发现孤立帖子，club_id {post_club_id} 未找到对应社团: {entry}")
                except json.JSONDecodeError as e:
                    logger.error(f"解析 local_synced_data.jsonl 中的JSON行错误: {line.strip()} - {e}")
                except Exception as e:
                    logger.error(f"处理 local_synced_data.jsonl 中的行时发生未知错误: {line.strip()} - {e}")
    except Exception as e:
        logger.error(f"读取本地同步数据文件失败: {LOCAL_SYNCED_DATA_FILE} - {e}")
    
    return clubs_data

@app.post("/club_recommend", response_model=Club_Recommend_Response)
async def club_recommend(request: Club_Recommend_Request):
    """
    社团推荐助手 - 根据用户信息推荐社团。
    根据用户信息，AI推荐适合的社团。
    """
    try:
        clubs_data = load_local_synced_data()
        
        if not clubs_data:
            raise HTTPException(status_code=404, detail="未找到社团信息进行推荐。")

        # 准备社团信息字符串，用于LLM的Prompt
        club_info_str = []
        for club_id, club in clubs_data.items():
            club_name = club.get("club_name", f"未知社团 {club_id}")
            description = club.get("description", "无描述")
            tags = ", ".join(club.get("tags", [])) if club.get("tags") else "无标签"
            posts_summary = ""
            if club.get("posts"):
                post_titles = [post.get("title", post.get("document", "无标题")) for post in club["posts"]]
                posts_summary = "，相关帖子有：" + "，".join(post_titles[:3]) + ("..." if len(post_titles) > 3 else "")
            
            club_info_str.append(f"""社团名称: {club_name}\n描述: {description}\n标签: {tags}{posts_summary}\n""")

        clubs_list_for_prompt = "\n---\n".join(club_info_str)

        prompt_template = """
你是一个智能社团推荐助手。你的任务是根据用户的个人信息、兴趣标签和专业，从我提供的社团列表中，智能推荐最适合用户的社团。
对于每个推荐的社团，请说明推荐理由。

请按照以下JSON格式返回结果：
{{
  \"Summary_text\": \"[AI生成的推荐总结，概括推荐理由]\",
  \"Recommend_club_list\": [
    {{
      \"club_name\": \"[社团名称]\",
      \"description\": \"[社团描述]\",
      \"tags\": [\"[标签1]\", \"[标签2]\"],
      \"recommend_reason\": \"[推荐该社团的理由]\"
    }},
    // 可以推荐多个社团
  ]
}}

--- 用户信息 ---
用户姓名: {user_name}
用户个人描述: {user_description}
用户兴趣标签: {user_tags}
用户专业: {user_major}

--- 可选社团列表 ---
{clubs_list}

请开始生成社团推荐。
"""
        user_tags_str = ", ".join(request.User_tags) if request.User_tags else "无"

        full_prompt = prompt_template.format(
            user_name=request.User_name,
            user_description=request.User_description,
            user_tags=user_tags_str,
            user_major=request.User_major,
            clubs_list=clubs_list_for_prompt
        )

        logger.info(f"AI社团推荐Prompt: {full_prompt[:200]}...")

        llm_response_content = ""
        for chunk in tongyi_chat_embedded(messages=full_prompt):
            if chunk.get("type") == "content":
                llm_response_content += chunk.get("content", "")
            elif chunk.get("type") == "error":
                raise Exception(chunk.get("content", "AI生成服务错误"))

        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        json_string = llm_response_content.strip()
        if json_string.startswith("```json") and json_string.endswith("```"):
            json_string = json_string[len("```json"): -len("```")].strip()

        try:
            parsed_response = json.loads(json_string)
            summary_text = parsed_response.get("Summary_text", "")
            recommend_club_list_data = parsed_response.get("Recommend_club_list", [])

            if not summary_text or not isinstance(recommend_club_list_data, list):
                raise ValueError("AI返回的JSON格式不完整或字段类型不正确。")

            recommend_club_list = []
            for club_data in recommend_club_list_data:
                try:
                    club_info = ClubInfo(**club_data)
                    recommend_club_list.append(club_info)
                except Exception as e:
                    logger.warning(f"解析单个推荐社团信息时出错: {club_data}, 错误: {e}")

            return Club_Recommend_Response(
                Summary_text=summary_text.strip(),
                Recommend_club_list=recommend_club_list
            )

        except json.JSONDecodeError:
            logger.error(f"AI响应不是有效的JSON: {llm_response_content}")
            raise ValueError(f"AI返回的响应格式错误，无法解析为JSON: {llm_response_content[:100]}...")

    except Exception as e:
        logger.error(f"AI社团推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI社团推荐失败: {e}")

@app.post("/update_club_data")
async def update_club_data_endpoint():
    """手动触发更新社团信息。"""
    logger.info("收到更新社团信息的请求...")
    try:
        result = await update_club_information()
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"手动更新社团信息接口失败: {e}")
        raise HTTPException(status_code=500, detail=f"手动更新社团信息接口失败: {e}")

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
    print(f"配置重载接口: http://{config.server_host}:{config.server_port}/reload_config")
    print(f"智能申请筛选接口: http://{config.server_host}:{config.server_port}/screen_application")
    print(f"社团氛围透视接口: http://{config.server_host}:{config.server_port}/club_atmosphere")
    print(f"智能活动策划接口: http://{config.server_host}:{config.server_port}/plan_event")
    print(f"智能财务助理接口: http://{config.server_host}:{config.server_port}/financial_bookkeeping")
    print(f"财务报表生成接口: http://{config.server_host}:{config.server_port}/generate_financial_report")
    print(f"预算超支预警接口: http://{config.server_host}:{config.server_port}/budget_warning")
    print(f"修改预算接口: http://{config.server_host}:{config.server_port}/update_budget")
    print(f"社团推荐接口: http://{config.server_host}:{config.server_port}/club_recommend")
    print(f"更新社团信息接口: http://{config.server_host}:{config.server_port}/update_club_data")
    
    uvicorn.run(
        app,
        host=config.server_host,
        port=config.server_port,
        log_level=config.log_level.lower()
    ) 