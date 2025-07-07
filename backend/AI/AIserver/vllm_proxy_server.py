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
from fastapi.responses import StreamingResponse, JSONResponse
import time
import re
import signal
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import httpx

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

# 全局变量用于控制服务器状态
server_should_exit = False
active_tasks = set()
shutdown_event = asyncio.Event()

def handle_exit_signal(signum, frame):
    """处理退出信号"""
    global server_should_exit
    signal_name = signal.Signals(signum).name
    logger.info(f"收到退出信号 {signal_name}，开始优雅停机...")
    server_should_exit = True
    
    # 如果在异步上下文中，设置关闭事件
    try:
        asyncio.get_event_loop().call_soon_threadsafe(shutdown_event.set)
    except Exception:
        pass

def check_exit():
    """检查是否应该退出"""
    if server_should_exit:
        logger.info(f"正在等待 {len(active_tasks)} 个活跃任务完成...")
        # 等待所有活跃任务完成
        while active_tasks:
            time.sleep(0.1)
        logger.info("所有任务已完成，服务器正在关闭...")
        sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, handle_exit_signal)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit_signal)  # kill

app = FastAPI(
    title="vLLM Proxy Server",
    description="一个用于转发请求到vLLM服务器的代理服务器",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """服务器启动时的初始化"""
    global server_should_exit, active_tasks
    server_should_exit = False
    active_tasks.clear()

@app.on_event("shutdown")
async def shutdown_event():
    """服务器关闭时的清理"""
    global server_should_exit
    server_should_exit = True
    logger.info("等待所有任务完成...")
    while active_tasks:
        await asyncio.sleep(0.1)
    logger.info("所有任务已完成")

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

# New Pydantic Models for ML data generation
class CommunityItem(BaseModel):
    community_id: int
    community_name: str
    tags: str # Pipe-separated string like 'photography|camera|artistic'

class UserItem(BaseModel):
    user_id: int
    user_tags: str # Pipe-separated string like '喜欢拍照|艺术创作|风景'

class InteractionItem(BaseModel):
    user_id: int
    community_id: int
    interaction: int # Assuming 1 for interaction
    timestamp: str # ISO format string for datetime

class MLDataGenerationRequest(BaseModel):
    num_communities: int = 5
    num_users: int = 5
    num_interactions: int = 8
    save_file: Optional[str] = "ml_data.json" # 新增保存文件名

class MLDataGenerationResponse(BaseModel):
    communities: List[CommunityItem]
    users: List[UserItem]
    interactions: List[InteractionItem]
    message: str # 新增消息字段
    file_path: Optional[str] = None # 新增保存文件路径字段

# New Pydantic Models for User data generation
class UserItem(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    created_at: str
    updated_at: str
    last_active_at: str
    extension: Dict[str, Any]

class UserDataGenerationRequest(BaseModel):
    num_users: int = 5
    save_file: Optional[str] = "user_data.jsonl"

class UserDataGenerationResponse(BaseModel):
    generated_count: int
    message: str
    sample_data: List[UserItem]
    file_path: Optional[str] = None

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
        max_tokens=max_tokens,
        stream=False
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

@app.post("/content", response_model=ContentGenerationResponse)
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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一位文案创作大师，擅长运用多种文体风格进行改写。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed for content length
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        generated_text = chat_response.response

        if not generated_text.strip():
            raise ValueError("AI未返回有效的生成内容。")
            
        return ContentGenerationResponse(generated_text=generated_text.strip())

    except Exception as e:
        logger.error(f"AI内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI内容生成失败: {e}")
@app.post("/introduction", response_model=ContentGenerationResponse)
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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一位文案创作大师，擅长运用多种文体风格进行改写。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed for content length
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        generated_text = chat_response.response

        if not generated_text.strip():
            raise ValueError("AI未返回有效的生成内容。")
            
        return ContentGenerationResponse(generated_text=generated_text.strip())

    except Exception as e:
        logger.error(f"AI内容生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI内容生成失败: {e}")

@app.post("/Slogan", response_model=ContentGenerationResponse)
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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你擅长写宣传口号：1.简短有力；2.突出亮点；3.引发共鸣。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed for slogan length
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        generated_text = chat_response.response

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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一个智能社团申请筛选助手，你的任务是根据申请者的资料和社团的招新要求，对申请进行评估，并生成简洁的摘要和明确的建议。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        llm_response_content = chat_response.response

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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一个社团氛围透视镜AI，你的任务是根据社团内部的交流内容，分析其情感和主题，并生成社团的\"氛围标签\"和一段\"文化摘要\"."),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        llm_response_content = chat_response.response

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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一个智能活动策划参谋AI，你的任务是根据用户提供的活动想法，生成一份详尽的策划框架。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        llm_response_content = chat_response.response

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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一个智能财务助理，你的任务是根据用户输入的自然语言描述，解析出财务支出或收入的详细信息，并生成结构化的记账条目和友好的确认信息。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        llm_response_content = chat_response.response

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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一个智能财务报表生成助手，你的任务是根据用户提供的财务流水，生成一份清晰、专业的财务报表总结，并详细列出各项支出和收入的分类汇总。请注意，这里主要是支出，如果出现收入字样可以进行分类。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        llm_response_content = chat_response.response

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
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一个预算管理助手，你的任务是根据当前的支出和预算限额，判断是否超支，并生成一个友好的预警信息。如果用户提供了描述信息，请在预警信息中提及。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        llm_response_content = chat_response.response

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

# 添加推荐服务的配置
RECOMMENDATION_SERVICE_URL = "http://localhost:8001"

@app.post("/club_recommend", response_model=Club_Recommend_Response)
async def club_recommend(request: Club_Recommend_Request):
    """
    社团推荐助手 - 根据用户信息推荐社团。
    结合AI推荐系统和大语言模型，为用户推荐适合的社团。
    """
    try:
        # 1. 首先获取基于内容的推荐结果
        user_profile = {
            "user_id": request.User_name,
            "interests": request.User_description,
            "major": request.User_major,
            "tags": request.User_tags
        }
        
        recommendations = None
        try:
            # 调用推荐服务
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{RECOMMENDATION_SERVICE_URL}/recommend",
                    json=user_profile,
                    timeout=5.0  # 5秒超时
                )
                if response.status_code == 200:
                    recommendations = response.json()
        except Exception as e:
            logger.warning(f"推荐系统调用失败，将继续使用AI推荐: {str(e)}")

        # 2. 获取社团信息
        clubs_data = load_local_synced_data()
        if not clubs_data:
            raise HTTPException(status_code=404, detail="未找到社团信息进行推荐。")

        # 3. 准备社团信息字符串
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

        # 4. 准备推荐系统结果的提示词
        recommendation_prompt = ""
        if recommendations and recommendations.get("recommendations"):
            recommendation_prompt = "\n\n--- 推荐系统的建议（仅供参考） ---\n"
            for idx, rec in enumerate(recommendations["recommendations"], 1):
                score = float(rec.get("similarity_score", 0)) * 100
                recommendation_prompt += f"{idx}. {rec['club_name']} (匹配度: {score:.1f}%)\n"
                recommendation_prompt += f"   标签: {rec['tags']}\n"
                recommendation_prompt += f"   描述: {rec['desc']}\n\n"

        # 5. 构建完整的提示词
        prompt_template = """
你是一个智能社团推荐助手。你的任务是根据用户的个人信息、兴趣标签和专业，从我提供的社团列表中，智能推荐最适合用户的社团。
对于每个推荐的社团，请说明推荐理由。

请注意：
1. 推荐系统的建议仅供参考，你应该根据用户的具体情况和社团的详细信息做出独立判断
2. 可以选择推荐系统建议的社团，也可以推荐其他更适合的社团
3. 重点关注用户的兴趣、专业和社团的实际活动内容的匹配度

请按照以下JSON格式返回结果：
{{
  "Summary_text": "[AI生成的推荐总结，概括推荐理由]",
  "Recommend_club_list": [
    {{
      "club_name": "[社团名称]",
      "description": "[社团描述]",
      "tags": ["[标签1]", "[标签2]"],
      "recommend_reason": "[推荐该社团的理由]"
    }},
    // 可以推荐多个社团
  ]
}}

--- 用户信息 ---
用户姓名: {user_name}
用户个人描述: {user_description}
用户兴趣标签: {user_tags}
用户专业: {user_major}
{recommendation_prompt}
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
            recommendation_prompt=recommendation_prompt,
            clubs_list=clubs_list_for_prompt
        )

        logger.info(f"AI社团推荐Prompt: {full_prompt[:200]}...")

        # 6. 调用AI生成推荐
        llm_response_content = ""
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一个智能社团推荐助手，你的任务是根据用户的个人信息、兴趣标签和专业，从我提供的社团列表中，智能推荐最适合用户的社团。对于每个推荐的社团，请说明推荐理由。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        llm_response_content = chat_response.response

        if not llm_response_content.strip():
            raise ValueError("AI未返回有效的响应内容。")

        # 7. 解析AI响应
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

# 新增训练数据生成请求和响应模型
class TrainingDataGenerationRequest(BaseModel):
    batch_size: int = 10
    total_count: int = 100
    save_file: Optional[str] = "training_data.jsonl"
    data_type: Optional[str] = "general"  # 可选值: "general", "knowledge" 或 "faq"

class TrainingDataGenerationResponse(BaseModel):
    generated_count: int
    message: str
    sample_data: List[Dict[str, str]]

@app.post("/generate_training_data", response_model=TrainingDataGenerationResponse)
async def generate_training_data(request: TrainingDataGenerationRequest):
    task_id = id(request)  # 使用请求对象的id作为任务id
    active_tasks.add(task_id)
    try:
        prompt_template = """# 角色
你是一名顶尖的AI微调数据生成专家，专门为"大学社团管理AI助手"项目创建高质量的训练数据。

# 任务
请一次性生成{batch_size}条高质量的社团管理场景训练数据。每条数据都应该模拟一个真实的社团管理场景。
注意：必须一次性生成完整的{batch_size}条数据，不要分批生成。

# 角色指令模板（每个模板应该被大致相等次数使用）

1. 社团管理员视角（约占20%）：
- "你是一名经验丰富的社团管理员，请简洁、专业地回答以下成员提问。"
- "作为社团的管理层成员，请针对以下问题提供专业的解决方案。"
- "你是社团的活动主管，请就以下活动相关问题给出建议。"

2. 社长/副社长视角（约占20%）：
- "作为社团的最高负责人，请对以下情况作出决策和指导。"
- "你是一位富有经验的社团社长，请为以下管理问题提供战略性建议。"
- "作为社团领导者，请针对以下社团发展问题给出你的规划。"

3. 普通社员视角（约占20%）：
- "作为一名普通社员，请基于你的经验回答其他成员的疑问。"
- "你是一位积极参与社团活动的成员，请分享你的见解。"
- "作为社团的老成员，请为新成员解答以下问题。"

4. 新成员/潜在成员视角（约占20%）：
- "作为一名新加入的成员，请提供你对以下社团事务的理解和建议。"
- "你是一位即将加入社团的新成员，请就以下入社相关问题寻求帮助。"
- "作为对社团感兴趣的同学，请提出你的疑问和想法。"

5. 跨部门协作视角（约占20%）：
- "作为多个部门之间的协调者，请针对以下合作问题提供解决方案。"
- "你同时参与多个社团项目，请就以下跨部门协作问题提供建议。"
- "作为部门间的沟通桥梁，请协调解决以下问题。"

# 数据格式要求
必须严格按照以下格式生成数据，instruction必须从上述模板中选择，不能自行发明：
[
  {{
    "instruction": "你是一名经验丰富的社团管理员，请简洁、专业地回答以下成员提问。",
    "input": "如何优化社团的财务管理流程？",
    "output": "建议从以下几个方面入手：1. 建立电子账本，详细记录收支；2. 设置预算审批制度；3. 定期公示财务状况；4. 建立报销规范流程；5. 每月进行财务分析。"
  }},
  {{
    "instruction": "作为社团的最高负责人，请对以下情况作出决策和指导。",
    "input": "社团成员之间出现了分歧，影响了活动进展，该如何处理？",
    "output": "1. 立即召开内部会议了解情况；2. 分别与相关成员沟通，听取各方意见；3. 制定折中方案，平衡各方诉求；4. 明确任务优先级，确保活动正常进行；5. 建立长期沟通机制，预防类似问题。"
  }},
  // ... 继续生成，直到达到{batch_size}条数据 ...
]

# 生成要求
1. 必须一次性生成完整的{batch_size}条数据
2. instruction字段必须从上述模板中直接复制，不能改变或发明新的
3. 确保每个角色视角生成约 {role_count} 条数据（{batch_size}的20%）
4. 每个角色下的3个模板使用次数应接近 {template_count} 次
5. 确保生成的是一个有效的JSON数组，包含完整的{batch_size}条数据
6. input必须是具体的问题，output必须是专业且实用的回答

请直接返回一个包含{batch_size}条数据的完整JSON数组，不要包含任何其他文本。"""

        # 知识信息查询类问题的prompt模板
        knowledge_prompt_template = """你是一名严谨、专业的大学社团信息查询AI助手，专注于为用户提供清晰、准确、具体的社团相关知识性信息。

你的任务是为大学社团场景生成**真实、准确且高质量的信息查询问答对**，每个问答对必须是独立的，且`output`应直接针对`input`给出答案，不包含额外说明或寒暄。

**场景约束**：仅限于大学社团的常见知识和信息查询，包括但不限于：
1.  **社团简介**：如社团的成立时间、主要活动、特色、联系方式等。
2.  **规章制度解读**：如社团注册规定、经费使用细则、活动审批流程中的具体条款等。
3.  **资源信息**：如可用的活动场地、宣传渠道、物资借用流程等。
4.  **历史数据**：如往届社团评优结果、经典活动回顾等（使用占位符）。

**生成要求**：
* 所有信息必须具体化，禁止出现模糊表述。
* 涉及名称、日期、地点、联系方式等信息时，请使用占位符（如"XXXX年XX月XX日"、"活动中心X楼X室"、"邮箱xxx@xxx.com"、"电话13X XXXX XXXX"）。
* 避免生成重复或逻辑错误的问答。

请一次性生成{batch_size}条高质量的社团知识信息查询数据。每条数据都应该模拟一个真实的社团信息查询场景。
注意：必须一次性生成完整的{batch_size}条数据，不要分批生成。

请严格按照以下JSON格式输出，不要包含任何额外文字、说明或代码注释，直接输出JSON数组：

[
  {{
    "instruction": "请作为社团信息管理员，为用户提供关于指定社团的详细介绍。",
    "input": "请介绍一下学校的摄影社。",
    "output": "学校摄影社成立于XXXX年，是一个汇集摄影爱好者的艺术社团，致力于提升成员的摄影技术和审美能力。社团每周X在教学楼A座X楼举办主题分享会和作品点评，定期组织外拍活动，并承办校园各项活动的摄影记录工作。社长联系方式：XXX，社团官方邮箱：photo.club@xxx.edu.cn。"
  }},
  {{
    "instruction": "请作为规章制度专家，详细解释社团经费使用规定中的具体条款。",
    "input": "社团经费中，购买固定资产的上限是多少？",
    "output": "根据《XXX大学学生社团经费管理办法》第五条规定，社团使用经费购买单项价值超过XXX元的固定资产，需提前向社团联合会提交申请，并经审批同意后方可执行。年度内累计购买固定资产总额不得超过社团年度总预算的XX%。"
  }}
]

# 生成要求
1. 必须一次性生成完整的{batch_size}条数据
2. 确保生成的是一个有效的JSON数组，包含完整的{batch_size}条数据
3. input必须是具体的问题，output必须是专业且实用的回答

请直接返回一个包含{batch_size}条数据的完整JSON数组，不要包含任何其他文本。"""

        # FAQ类问题的prompt模板
        faq_prompt_template = """你是一名经验丰富的社团问题解决专家，专注于为用户提供简洁、专业且具有可操作性的故障排除和常见问题解答。

你的任务是为大学社团场景生成**真实、具体且高质量的常见问题解答对**，每个问答对必须是独立的，且`output`应直接针对`input`给出解决方案或指引，不包含额外说明或寒暄。

**场景约束**：仅限于大学社团运营中常见的系统问题、流程障碍、突发情况及日常疑问，包括但不限于：
1.  **系统使用问题**：如登录失败、文件上传错误、信息提交不成功等。
2.  **流程卡滞问题**：如审批进度异常、材料提交不符合要求、流程中断等。
3.  **日常操作疑问**：如社团邮箱密码忘记、活动物料遗失、通知未能及时送达等。
4.  **轻微突发状况**：如活动现场设备故障、报名人数不足等。

**生成要求**：
* 所有解决方案必须具体、可执行，禁止出现模糊或无效的指引。
* 涉及联系方式、具体部门、系统模块等信息时，请使用占位符（如"联系社联办公室（电话：12345678）"、"登录社团管理系统'反馈'模块"、"行政楼X楼X室"）。
* 避免生成重复或逻辑错误的问答。

请一次性生成{batch_size}条高质量的社团FAQ数据。每条数据都应该模拟一个真实的社团问题解决场景。
注意：必须一次性生成完整的{batch_size}条数据，不要分批生成。

请严格按照以下JSON格式输出，不要包含任何额外文字、说明或代码注释，直接输出JSON数组：

[
  {{
    "instruction": "请作为社团系统技术支持，指导用户解决常见的系统操作问题。",
    "input": "我在社团管理系统登录时总是显示"密码错误"，但我的密码是正确的，怎么办？",
    "output": "1. 确认大小写锁定键是否开启。2. 尝试使用"忘记密码"功能重置密码。3. 如果问题仍然存在，请清除浏览器缓存和Cookie后重试。4. 若以上方法无效，请联系学校信息技术中心（电话：12345678）或社联技术支持邮箱（tech@xxx.edu.cn）寻求帮助。"
  }},
  {{
    "instruction": "请作为流程顾问，帮助用户理解并解决审批流程中的疑问。",
    "input": "我的社团活动场地申请提交一周了，还没有任何审批进展，该怎么办？",
    "output": "通常场地申请的审批周期为3个工作日。若已超过一周仍无进展，建议您：1. 登录社团管理系统，进入"我的申请"查看具体审批状态及反馈。2. 确认是否所有附件（如活动策划书）都已完整上传。3. 直接联系学校场地管理中心（电话：12345678）或相关审批负责人查询进度。"
  }}
]

# 生成要求
1. 必须一次性生成完整的{batch_size}条数据
2. 确保生成的是一个有效的JSON数组，包含完整的{batch_size}条数据
3. input必须是具体的问题，output必须是专业且实用的回答

请直接返回一个包含{batch_size}条数据的完整JSON数组，不要包含任何其他文本。"""

        # 计算每种类型应该生成的数量
        role_count = request.batch_size // 5  # 每个角色视角的数量
        topic_count = request.batch_size // 5  # 每个主题的数量
        template_count = role_count // 3  # 每个模板的使用次数
        
        # 格式化提示词
        current_prompt = None
        if request.data_type == "knowledge":
            current_prompt = knowledge_prompt_template.format(
                batch_size=request.batch_size
            )
        elif request.data_type == "faq":
            current_prompt = faq_prompt_template.format(
                batch_size=request.batch_size
            )
        else:  # 默认使用general模板
            current_prompt = prompt_template.format(
                batch_size=request.batch_size,
                role_count=role_count,
                topic_count=topic_count,
                template_count=template_count
            )

        total_generated = 0
        all_data = []
        
        while total_generated < request.total_count and not server_should_exit:
            batch_size = min(request.batch_size, request.total_count - total_generated)
            
            # 实际生成的数量比请求的多2条，因为前两条会被忽略
            actual_batch_size = batch_size + 2
            
            # 计算每种类型应该生成的数量
            role_count = actual_batch_size // 5  # 每个角色视角的数量
            topic_count = actual_batch_size // 5  # 每个主题的数量
            template_count = role_count // 3  # 每个模板的使用次数
            
            # 格式化提示词
            current_prompt = None
            if request.data_type == "knowledge":
                current_prompt = knowledge_prompt_template.format(
                    batch_size=actual_batch_size
                )
            elif request.data_type == "faq":
                current_prompt = faq_prompt_template.format(
                    batch_size=actual_batch_size
                )
            else:  # 默认使用general模板
                current_prompt = prompt_template.format(
                    batch_size=actual_batch_size,
                    role_count=role_count,
                    topic_count=topic_count,
                    template_count=template_count
                )

            # 检查是否应该退出
            check_exit()
            
            # 构造发送给vLLM的payload
            payload = {
                "model": config.default_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专业的训练数据生成助手。请严格按照要求的JSON格式生成数据。"
                    },
                    {
                        "role": "user",
                        "content": current_prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.95,
                "max_tokens": 8000,
                "stream": True
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # 收集完整的响应
            llm_response_content = ""
            try:
                response = requests.post(
                    config.vllm_api_url,
                    headers=headers,
                    json=payload,
                    stream=True,
                    timeout=300  # 增加超时时间到5分钟
                )
                response.raise_for_status()
                
                # 使用更健壮的SSE处理
                buffer = ""
                for line in response.iter_lines():
                    if not line:
                        continue
                        
                    line = line.decode('utf-8')
                    if not line.startswith("data: "):
                        continue
                        
                    # 移除"data: "前缀
                    data = line[6:]
                    if data == "[DONE]":
                        break
                        
                    try:
                        json_data = json.loads(data)
                        if json_data.get("choices") and len(json_data["choices"]) > 0:
                            choice = json_data["choices"][0]
                            if choice.get("delta") and "content" in choice["delta"]:
                                content = choice["delta"]["content"]
                                llm_response_content += content
                                buffer += content
                    except json.JSONDecodeError:
                        logger.debug(f"无法解析的SSE数据行: {data}")
                        continue
                    except Exception as e:
                        logger.warning(f"处理流式响应数据时出错: {e}")
                        continue
                            
            except requests.exceptions.RequestException as e:
                logger.error(f"请求vLLM服务失败: {e}")
                continue
            except Exception as e:
                logger.error(f"生成过程出错: {e}")
                continue
            
            if not llm_response_content.strip():
                logger.warning("本批次生成的内容为空，跳过")
                continue

            # 清理响应文本并尝试解析
            json_string = llm_response_content.strip()
            
            # 记录原始响应以便调试
            logger.debug(f"原始响应: {json_string[:200]}...")
            
            try:
                # 如果响应已经是一个有效的JSON数组，直接解析
                if json_string.startswith('[') and json_string.endswith(']'):
                    try:
                        batch_data = json.loads(json_string)
                    except json.JSONDecodeError:
                        # 如果解析失败，尝试清理JSON字符串
                        json_string = re.sub(r',\s*]$', ']', json_string)
                        json_string = re.sub(r'^\[\s*,', '[', json_string)
                        batch_data = json.loads(json_string)
                else:
                    # 如果响应不是直接的JSON数组，尝试提取
                    start_idx = json_string.find('[')
                    end_idx = json_string.rfind(']')
                    
                    if start_idx == -1 or end_idx == -1:
                        logger.warning(f"响应中未找到JSON数组标记: {json_string[:200]}...")
                        continue
                    
                    json_string = json_string[start_idx:end_idx + 1]
                    json_string = re.sub(r',\s*]$', ']', json_string)
                    json_string = re.sub(r'^\[\s*,', '[', json_string)
                    batch_data = json.loads(json_string)
                
                if not isinstance(batch_data, list):
                    logger.warning(f"解析结果不是JSON数组: {type(batch_data)}")
                    continue
                
                # 验证每条数据的格式
                valid_data = []
                invalid_count = 0
                for i, item in enumerate(batch_data):
                    try:
                        # 跳过前两条数据
                        if i < 2:
                            continue
                            
                        if not all(key in item for key in ["instruction", "input", "output"]):
                            invalid_count += 1
                            continue
                        if not all(isinstance(item[key], str) for key in ["instruction", "input", "output"]):
                            invalid_count += 1
                            continue
                        valid_data.append(item)
                    except Exception as e:
                        invalid_count += 1
                        continue
                
                if invalid_count > 0:
                    logger.debug(f"本批次有 {invalid_count} 条无效数据被过滤（包括前两条示例数据）")
                
                if valid_data:
                    all_data.extend(valid_data)
                    total_generated += len(valid_data)
                    
                    # 保存到文件
                    if request.save_file:
                        save_path = os.path.join(current_dir, "generated_data", request.save_file)
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        with open(save_path, 'a', encoding='utf-8') as f:
                            for item in valid_data:
                                json.dump(item, f, ensure_ascii=False)
                                f.write('\n')
                    
                    logger.info(f"已生成 {total_generated}/{request.total_count} 条数据")
                else:
                    logger.warning("本批次所有数据都无效")
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON解析错误: {e}, 响应内容: {json_string[:200]}...")
                continue
            except Exception as e:
                logger.warning(f"处理本批次数据时出错: {e}")
                continue

        if not all_data:
            raise ValueError("未能生成任何有效数据")

        return TrainingDataGenerationResponse(
            generated_count=total_generated,
            message=f"成功生成 {total_generated} 条训练数据" + 
                   (f"并保存到 {request.save_file}" if request.save_file else "") +
                   (" (因收到退出信号提前结束)" if server_should_exit else ""),
            sample_data=all_data[:3]
        )

    except Exception as e:
        logger.error(f"生成训练数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成训练数据失败: {e}")
    finally:
        active_tasks.remove(task_id)

@app.post("/generate/activity_post", response_model=ContentGenerationResponse)
async def generate_activity_post(request: ContentGenerationRequest):
    """
    根据社团活动的实际开展情况，生成活动总结性质的社团动态。
    
    Args:
        request: 包含活动内容、文风和效果要求的请求体。
        content应包含：活动名称、时间地点、参与人数、活动过程、活动亮点、反馈等信息。
        
    Returns:
        ContentGenerationResponse: 包含生成的动态文本。
    """
    try:
        prompt_template = """你是一位专业的社团活动总结撰写专家，擅长将活动的实际开展情况转化为引人入胜的社交媒体动态。
请根据我提供的活动总结内容{content}，以{style}的文风进行改写，确保改写后的内容能达到{expection}的效果。

要求：
1. 突出活动的实际效果和价值
2. 展现参与者的收获和感受
3. 总结活动的精彩瞬间和亮点
4. 适当引用参与者的反馈或感言
5. 体现社团的专业性和影响力
6. 为后续活动预热（如有类似活动计划）
7. 增加适当的emoji表情增强表现力
8. 适当添加图片位置提示（如：[此处可插入活动现场照片]）
9. 添加合适的话题标签

重点描述：
- 活动实际效果
- 参与者反馈
- 精彩瞬间
- 社团价值
- 未来展望"""
        
        # 格式化Prompt
        full_prompt = prompt_template.format(
            content=request.content,
            style=request.style,
            expection=request.expection
        )
        
        logger.info(f"生成社团动态总结Prompt: {full_prompt[:200]}...") # 增加日志长度

        generated_text = ""
        # Construct messages for the chat function
        messages = [
            Message(role="system", content="你是一位专业的社团活动总结撰写专家，擅长将活动的实际开展情况转化为引人入胜的社交媒体动态。"),
            Message(role="user", content=full_prompt)
        ]
        
        chat_request = ChatRequest(
            messages=messages,
            model=config.default_model, # Use default model
            max_tokens=2048, # Adjust max tokens as needed for post length
            temperature=0.7,
            top_p=0.95,
            stream=False # We need a complete response
        )

        chat_response = await chat(chat_request) # Call the local chat function

        generated_text = chat_response.response

        if not generated_text.strip():
            raise ValueError("AI未返回有效的生成内容。")
            
        return ContentGenerationResponse(generated_text=generated_text.strip())

    except Exception as e:
        logger.error(f"AI社团动态总结生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI社团动态总结生成失败: {e}")

@app.post("/generate_ml_data", response_model=MLDataGenerationResponse)
async def generate_ml_data(request: MLDataGenerationRequest):
    """
    根据机器学习需求，使用AI生成模拟的社团、用户和互动数据。
    生成过程分为三个阶段：社团信息、个人偏好、以及基于前两者的互动信息。
    
    Args:
        request: 包含生成数量（社团、用户、互动）的请求体。
        
    Returns:
        MLDataGenerationResponse: 包含生成的社团、用户和互动数据。
    """
    try:
        # 固定每个批次LLM调用生成数量（为了多样性）
        LLM_BATCH_SIZE = 10 # 统一批次大小，LLM返回的实际数量会是这个值减2

        all_communities = []
        all_users = []
        all_interactions = []

        # 定义三个独立的Prompt模板
        community_prompt_template = """
你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟社团数据。
你的任务是根据以下数据模型和要求，一次性生成指定数量的模拟社团数据，并以JSON格式返回。

**重要：你必须生成与已提供数据不重复的全新数据。生成的 community_id 必须是未出现过的新ID。**

**数据模型:**
1.  **社团数据 (communities):**
    -   `community_id`: 整型，社团的唯一ID。
    -   `community_name`: 字符串，社团的名称。
    -   `tags`: 字符串，社团的标签，使用 '|' 分隔。可以是中文，数量不定，也可以没有（空字符串）。例如: '摄影|艺术|风景' 或 ''。

**生成数量要求:**
-   `num_communities`: {num_communities}

**已有社团数据 (请在此基础上生成新的、不重复的社团):**
{existing_data_str}

**输出格式要求:**
请**直接**按照以下JSON格式返回结果，**不要包含任何Markdown代码块或其他文本**：
{{
  "communities": [
    {{"community_id": 1, "community_name": "摄影社", "tags": "摄影|艺术|风景"}},
    {{"community_id": 2, "community_name": "篮球社", "tags": "篮球|运动|团队"}},
    // ... 其他社团数据 ...
  ]
}}

请开始生成数据。
"""

        user_prompt_template = """
你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户数据。
你的任务是根据以下数据模型和要求，一次性生成指定数量的模拟用户数据，并以JSON格式返回。

**重要：你必须生成与已提供数据不重复的全新数据。生成的 user_id 必须是未出现过的新ID。**

**数据模型:**
1.  **用户数据 (users):**
    -   `user_id`: 整型，用户的唯一ID。
    -   `user_tags`: 字符串，用户的兴趣标签，使用 '|' 分隔（可以是自定义的中文标签）。例如: '喜欢拍照|艺术创作|风景'。

**生成数量要求:**
-   `num_users`: {num_users}

**已有用户数据 (请在此基础上生成新的、不重复的用户):**
{existing_data_str}

**输出格式要求:**
请**直接**按照以下JSON格式返回结果，**不要包含任何Markdown代码块或其他文本**：
{{
  "users": [
    {{"user_id": 1, "user_tags": "喜欢拍照|艺术创作|风景"}},
    {{"user_id": 2, "user_tags": "运动健身|编程开发|团队协作"}},
    // ... 其他用户数据 ...
  ]
}}

请开始生成数据。
"""

        interaction_prompt_template = """
你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户-社团互动数据。
你的任务是根据以下数据模型和要求，一次性生成指定数量的模拟互动数据，并以JSON格式返回。

**重要：你必须生成与已提供数据不重复的全新数据。互动关系必须基于已提供的社团和用户ID来创建。**

**数据模型:**
1.  **用户-社团互动数据 (interactions):**
    -   `user_id`: 整型，参与互动的用户ID，**必须是已提供的 `users` 中的ID**。
    -   `community_id`: 整型，发生互动的社团ID，**必须是已提供的 `communities` 中的ID**。
    -   `interaction`: 整型，表示互动强度或类型，统一使用 `1`。
    -   `timestamp`: 字符串，互动发生的时间戳，使用 ISO 8601 格式 (例如: '2024-01-01T10:30:00Z')。

**生成数量要求:**
-   `num_interactions`: {num_interactions}

**已有社团信息 (可用于互动):**
{existing_communities_str}

**已有用户信息 (可用于互动):**
{existing_users_str}

**已有互动数据 (请在此基础上生成新的、不重复的互动):**
{existing_interactions_str}

**输出格式要求:**
请**直接**按照以下JSON格式返回结果，**不要包含任何Markdown代码块或其他文本**：
{{
  "interactions": [
    {{"user_id": 1, "community_id": 1, "interaction": 1, "timestamp": "2024-01-01T10:00:00Z"}},
    {{"user_id": 1, "community_id": 3, "interaction": 1, "timestamp": "2024-01-01T11:00:00Z"}},
    // ... 其他互动数据 ...
  ]
}}

请开始生成数据。
"""

        max_iterations = 100  # Adjust as needed, safety break

        # --- Stage 1: Generate Communities ---
        current_iteration = 0
        while len(all_communities) < request.num_communities and current_iteration < max_iterations:
            current_iteration += 1
            communities_to_request = min(LLM_BATCH_SIZE, request.num_communities - len(all_communities))

            if communities_to_request <= 0:
                break

            existing_communities_str = "\n".join([f"- ID: {c.community_id}, Name: {c.community_name}, Tags: {c.tags}" for c in all_communities]) if all_communities else "无"

            current_prompt_formatted = community_prompt_template.format(
                num_communities=communities_to_request + 2, # +2 for example discarding
                existing_data_str=existing_communities_str
            )
            
            logger.info(f"AI机器学习数据生成Prompt (Communities Iteration {current_iteration}): {current_prompt_formatted[:200]}...")

            messages = [
                Message(role="system", content="你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟社团数据。请严格按照要求的JSON格式返回数据。请确保生成的数据是全新的，并且ID不与提供的已有数据重复。"),
                Message(role="user", content=current_prompt_formatted)
            ]
            
            chat_request = ChatRequest(
                messages=messages,
                model=config.default_model,
                max_tokens=8000,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )

            llm_response_content = ""
            try:
                chat_response = await chat(chat_request)
                llm_response_content = chat_response.response
            except HTTPException as e:
                logger.warning(f"LLM调用失败 (Communities Iteration {current_iteration}): {e.detail}")
                continue
            except Exception as e:
                logger.warning(f"LLM调用发生未知错误 (Communities Iteration {current_iteration}): {e}")
                continue

            if not llm_response_content.strip():
                logger.warning(f"AI未返回有效的响应内容 (Communities Iteration {current_iteration})。")
                continue

            json_string = llm_response_content.strip()
            if json_string.startswith("```json") and json_string.endswith("```"):
                json_string = json_string[len("```json"): -len("```")].strip()
            
            match = re.search(r'"communities":\s*\[.*?\]', json_string, re.DOTALL) # More specific regex for communities list
            if not match:
                logger.warning(f"AI响应中未找到有效的communities JSON结构 (Communities Iteration {current_iteration}): {llm_response_content[:200]}...")
                continue
            
            try:
                # Extract only the communities array for parsing
                communities_array_str = "{\"communities\": " + match.group(0).split(':', 1)[1] + "}"
                parsed_response = json.loads(communities_array_str)
                communities_data = parsed_response.get("communities", [])

                existing_community_ids = {c.community_id for c in all_communities}
                new_communities_batch = []
                for item in communities_data[2:]:
                    try:
                        community = CommunityItem(**item)
                        if community.community_id not in existing_community_ids:
                            new_communities_batch.append(community)
                            existing_community_ids.add(community.community_id)
                        else:
                            logger.warning(f"Skipping duplicate community ID: {community.community_id} (Communities Iteration {current_iteration})")
                    except Exception as e:
                        logger.warning(f"解析单个社团条目时出错: {item}, 错误: {e} (Communities Iteration {current_iteration})")

                all_communities.extend(new_communities_batch)
                logger.info(f"Communities Iteration {current_iteration}: Added {len(new_communities_batch)} new communities. Total so far: {len(all_communities)}")

            except json.JSONDecodeError as e:
                logger.warning(f"AI响应不是有效的JSON (Communities Iteration {current_iteration}): {e}, 响应内容: {json_string[:200]}...")
                continue
            except Exception as e:
                logger.warning(f"处理本批次社团数据时出错 (Communities Iteration {current_iteration}): {e}")
                continue
        
        if not all_communities and request.num_communities > 0:
            raise ValueError("未能生成任何社团数据")
        
        # --- Stage 2: Generate Users ---
        current_iteration = 0
        while len(all_users) < request.num_users and current_iteration < max_iterations:
            current_iteration += 1
            users_to_request = min(LLM_BATCH_SIZE, request.num_users - len(all_users))

            if users_to_request <= 0:
                break

            existing_users_str = "\n".join([f"- ID: {u.user_id}, Tags: {u.user_tags}" for u in all_users]) if all_users else "无"

            current_prompt_formatted = user_prompt_template.format(
                num_users=users_to_request + 2, # +2 for example discarding
                existing_data_str=existing_users_str
            )
            
            logger.info(f"AI机器学习数据生成Prompt (Users Iteration {current_iteration}): {current_prompt_formatted[:200]}...")

            messages = [
                Message(role="system", content="你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户数据。请严格按照要求的JSON格式返回数据。请确保生成的数据是全新的，并且ID不与提供的已有数据重复。"),
                Message(role="user", content=current_prompt_formatted)
            ]
            
            chat_request = ChatRequest(
                messages=messages,
                model=config.default_model,
                max_tokens=8000,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )

            llm_response_content = ""
            try:
                chat_response = await chat(chat_request)
                llm_response_content = chat_response.response
            except HTTPException as e:
                logger.warning(f"LLM调用失败 (Users Iteration {current_iteration}): {e.detail}")
                continue
            except Exception as e:
                logger.warning(f"LLM调用发生未知错误 (Users Iteration {current_iteration}): {e}")
                continue

            if not llm_response_content.strip():
                logger.warning(f"AI未返回有效的响应内容 (Users Iteration {current_iteration})。")
                continue

            json_string = llm_response_content.strip()
            if json_string.startswith("```json") and json_string.endswith("```"):
                json_string = json_string[len("```json"): -len("```")].strip()
            
            match = re.search(r'"users":\s*\[.*?\]', json_string, re.DOTALL) # More specific regex for users list
            if not match:
                logger.warning(f"AI响应中未找到有效的users JSON结构 (Users Iteration {current_iteration}): {llm_response_content[:200]}...")
                continue
            
            try:
                # Extract only the users array for parsing
                users_array_str = "{\"users\": " + match.group(0).split(':', 1)[1] + "}"
                parsed_response = json.loads(users_array_str)
                users_data = parsed_response.get("users", [])

                existing_user_ids = {u.user_id for u in all_users}
                new_users_batch = []
                for item in users_data[2:]:
                    try:
                        user = UserItem(**item)
                        if user.user_id not in existing_user_ids:
                            new_users_batch.append(user)
                            existing_user_ids.add(user.user_id)
                        else:
                            logger.warning(f"Skipping duplicate user ID: {user.user_id} (Users Iteration {current_iteration})")
                    except Exception as e:
                        logger.warning(f"解析单个用户条目时出错: {item}, 错误: {e} (Users Iteration {current_iteration})")

                all_users.extend(new_users_batch)
                logger.info(f"Users Iteration {current_iteration}: Added {len(new_users_batch)} new users. Total so far: {len(all_users)}")

            except json.JSONDecodeError as e:
                logger.warning(f"AI响应不是有效的JSON (Users Iteration {current_iteration}): {e}, 响应内容: {json_string[:200]}...")
                continue
            except Exception as e:
                logger.warning(f"处理本批次用户数据时出错 (Users Iteration {current_iteration}): {e}")
                continue
        
        if not all_users and request.num_users > 0:
            raise ValueError("未能生成任何用户数据")

        # --- Stage 3: Generate Interactions ---
        current_iteration = 0
        # Collect all existing community and user IDs for the LLM to use
        available_community_ids = [c.community_id for c in all_communities]
        available_user_ids = [u.user_id for u in all_users]

        if not available_community_ids or not available_user_ids:
            logger.warning("没有足够的社团或用户数据来生成互动，跳过互动生成阶段。")
            # If interactions are requested but no communities/users, we should still return what we have.
            # raise ValueError("没有足够的社团或用户数据来生成互动") # Removed to allow partial generation

        while len(all_interactions) < request.num_interactions and current_iteration < max_iterations and available_community_ids and available_user_ids:
            current_iteration += 1
            interactions_to_request = min(LLM_BATCH_SIZE, request.num_interactions - len(all_interactions))

            if interactions_to_request <= 0:
                break

            existing_interactions_str = "\n".join([f"- UserID: {i.user_id}, CommunityID: {i.community_id}, Timestamp: {i.timestamp}" for i in all_interactions]) if all_interactions else "无"
            existing_communities_str_for_interactions = "\n".join([f"- ID: {c}" for c in available_community_ids])
            existing_users_str_for_interactions = "\n".join([f"- ID: {u}" for u in available_user_ids])

            current_prompt_formatted = interaction_prompt_template.format(
                num_interactions=interactions_to_request + 2, # +2 for example discarding
                existing_communities_str=existing_communities_str_for_interactions,
                existing_users_str=existing_users_str_for_interactions,
                existing_interactions_str=existing_interactions_str
            )
            
            logger.info(f"AI机器学习数据生成Prompt (Interactions Iteration {current_iteration}): {current_prompt_formatted[:200]}...")

            messages = [
                Message(role="system", content="你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户-社团互动数据。请严格按照要求的JSON格式返回数据。请确保生成的数据是全新的，并且互动关系必须基于提供的社团和用户ID来创建。"),
                Message(role="user", content=current_prompt_formatted)
            ]
            
            chat_request = ChatRequest(
                messages=messages,
                model=config.default_model,
                max_tokens=8000,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )

            llm_response_content = ""
            try:
                chat_response = await chat(chat_request)
                llm_response_content = chat_response.response
            except HTTPException as e:
                logger.warning(f"LLM调用失败 (Interactions Iteration {current_iteration}): {e.detail}")
                continue
            except Exception as e:
                logger.warning(f"LLM调用发生未知错误 (Interactions Iteration {current_iteration}): {e}")
                continue

            if not llm_response_content.strip():
                logger.warning(f"AI未返回有效的响应内容 (Interactions Iteration {current_iteration})。")
                continue

            json_string = llm_response_content.strip()
            if json_string.startswith("```json") and json_string.endswith("```"):
                json_string = json_string[len("```json"): -len("```")].strip()
            
            match = re.search(r'"interactions":\s*\[.*?\]', json_string, re.DOTALL) # More specific regex for interactions list
            if not match:
                logger.warning(f"AI响应中未找到有效的interactions JSON结构 (Interactions Iteration {current_iteration}): {llm_response_content[:200]}...")
                continue
            
            try:
                # Extract only the interactions array for parsing
                interactions_array_str = "{\"interactions\": " + match.group(0).split(':', 1)[1] + "}"
                parsed_response = json.loads(interactions_array_str)
                interactions_data = parsed_response.get("interactions", [])

                # For interactions, we need a way to check if an identical interaction (user_id, community_id, timestamp) already exists
                existing_interaction_tuples = {(i.user_id, i.community_id, i.timestamp) for i in all_interactions}
                
                new_interactions_batch = []
                for item in interactions_data[2:]:
                    try:
                        interaction = InteractionItem(**item)
                        interaction_tuple = (interaction.user_id, interaction.community_id, interaction.timestamp)

                        # Validate if the user_id and community_id exist in our *already generated and available* lists
                        if interaction.user_id in available_user_ids and \
                           interaction.community_id in available_community_ids and \
                           interaction_tuple not in existing_interaction_tuples:
                            new_interactions_batch.append(interaction)
                            existing_interaction_tuples.add(interaction_tuple)
                        else:
                            # Log why an interaction was skipped (e.g., invalid ID or duplicate)
                            if interaction_tuple in existing_interaction_tuples:
                                logger.warning(f"Skipping duplicate interaction: {interaction_tuple} (Interactions Iteration {current_iteration})")
                            else:
                                logger.warning(f"Skipping interaction with invalid user_id ({interaction.user_id}) or community_id ({interaction.community_id}) not found in available IDs. (Interactions Iteration {current_iteration})")
                    except Exception as e:
                        logger.warning(f"解析单个互动条目时出错: {item}, 错误: {e} (Interactions Iteration {current_iteration})")
                        continue
                
                all_interactions.extend(new_interactions_batch)
                logger.info(f"Interactions Iteration {current_iteration}: Added {len(new_interactions_batch)} new interactions. Total so far: {len(all_interactions)}")

            except json.JSONDecodeError as e:
                logger.warning(f"AI响应不是有效的JSON (Interactions Iteration {current_iteration}): {e}, 响应内容: {json_string[:200]}...")
                continue
            except Exception as e:
                logger.warning(f"处理本批次互动数据时出错 (Interactions Iteration {current_iteration}): {e}")
                continue

        # Final truncation to exact requested quantities
        final_communities = all_communities[:request.num_communities]
        final_users = all_users[:request.num_users]
        final_interactions = all_interactions[:request.num_interactions]

        if not final_communities and not final_users and not final_interactions:
            raise ValueError("未能生成任何有效数据")

        # Save to file
        save_path = None
        if request.save_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name, ext = os.path.splitext(request.save_file)
            file_name = f"{base_name}_{timestamp}{ext}" if ext else f"{base_name}_{timestamp}"
            save_path = os.path.join(current_dir, "generated_data", file_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            try:
                # Combine all data into a single structure for saving
                combined_data = {
                    "communities": [c.dict() for c in final_communities],
                    "users": [u.dict() for u in final_users],
                    "interactions": [i.dict() for i in final_interactions]
                }
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(combined_data, f, indent=2, ensure_ascii=False)
                logger.info(f"ML数据已成功保存到: {save_path}")
            except Exception as e:
                logger.error(f"保存ML数据到文件失败: {e}")
                save_path = None

        return MLDataGenerationResponse(
            communities=final_communities,
            users=final_users,
            interactions=final_interactions,
            message=f"成功生成 {len(final_communities)} 条社团数据, {len(final_users)} 条用户数据, {len(final_interactions)} 条互动数据",
            file_path=save_path
        )
            
    except Exception as e:
        logger.error(f"AI机器学习数据生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI机器学习数据生成失败: {e}")

@app.post("/generate_user_data", response_model=MLDataGenerationResponse)
async def generate_user_data(request: MLDataGenerationRequest):
    """
    根据机器学习需求，使用AI生成模拟的社团、用户和互动数据。
    生成过程分为三个阶段：社团信息、个人偏好、以及基于前两者的互动信息。
    
    Args:
        request: 包含生成数量（社团、用户、互动）的请求体。
        
    Returns:
        MLDataGenerationResponse: 包含生成的社团、用户和互动数据。
    """
    try:
        # 固定每个批次LLM调用生成数量（为了多样性）
        LLM_BATCH_SIZE = 10 # 统一批次大小，LLM返回的实际数量会是这个值减2

        all_users = []

        user_prompt_template = """
你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户数据。

你的任务是根据以下数据模型和要求，一次性生成指定数量的模拟用户数据，并以JSON格式返回。



**重要：你必须生成与已提供数据不重复的全新数据。生成的 user_id 必须是未出现过的新ID。**



**数据模型:**

-   `user_id`: 整型，用户的唯一ID。

-   `username`: 字符串，用户名，例如 "user_001", "admin_test"。

-   `email`: 字符串，电子邮件地址，例如 "user001@example.com"。

-   `role`: 字符串，角色类型，只能是 "user" 或 "admin"。

-   `created_at`: 字符串，创建时间，ISO 8601 格式，例如 "2024-01-01T10:00:00.000000"。

-   `updated_at`: 字符串，更新时间，ISO 8601 格式，通常晚于 created_at。

-   `last_active_at`: 字符串，最后活动时间，ISO 8601 格式，通常晚于 updated_at。

-   `extension`: JSON 对象字符串，包含用户的额外信息,包括interestedCategories，emailNotifications，applicationNotifications，activityNotifications，profilePublic，showJoinedClubs，tags,phone，包括例如: `{{\"realName\":\"张三\",\"studentId\":\"20230001\",\"major\":\"计算机学院\",\"bio\":\"热爱编程和篮球\",\"preferences\":{{\"interestedCategories\":[\"科技\",\"运动\"],\"emailNotifications\":true,\"applicationNotifications\":true,\"activityNotifications\":false,\"profilePublic\":true,\"showJoinedClubs\":true}},\"tags\":[\"开朗外向\",\"逻辑清晰\"],\"phone\":\"138xxxx1234\"}}`



**注意：**

-   `password` 和 `avatar_url` 字段无需生成，它们将由其他系统处理。

-   `user_id` 应从 1 开始递增，确保在当前批次中唯一。



**生成数量要求:**

-   `num_users`: {num_users}



**输出格式要求:**

请**直接**按照以下JSON格式返回结果，**不要包含任何Markdown代码块或其他文本**：

{{

  "users": [

    {{\"user_id\": 1, \"username\": \"testadmin\", \"email\": \"aabb@cc.com\", \"role\": \"admin\", \"created_at\": \"2025-06-24T16:04:30.705418\", \"updated_at\": \"2025-07-04T09:22:57.908024\", \"last_active_at\": \"2025-06-25T19:44:11.12609\", \"extension\": {{\"realName\":\"张三\",\"studentId\":\"20230001\",\"major\":\"计算机学院\",\"bio\":\"热爱编程和篮球\",\"preferences\":{{\"interestedCategories\":[\"科技\",\"运动\"],\"emailNotifications\":true,\"applicationNotifications\":true,\"activityNotifications\":false,\"profilePublic\":true,\"showJoinedClubs\":true}},\"tags\":[\"开朗外向\",\"逻辑清晰\"],\"phone\":\"138xxxx1234\"}}}},

    {{\"user_id\": 2, \"username\": \"normaluser\", \"email\": \"user@example.com\", \"role\": \"user\", \"created_at\": \"2025-06-25T10:00:00.000000\", \"updated_at\": \"2025-07-05T10:30:00.000000\", \"last_active_at\": \"2025-07-05T11:00:00.000000\", \"extension\": {{\"realName\":\"李四\",\"studentId\":\"20230002\",\"major\":\"软件工程\",\"bio\":\"喜欢户外活动\",\"preferences\":{{\"interestedCategories\":[\"户外\",\"音乐\"],\"emailNotifications\":true,\"applicationNotifications\":false,\"activityNotifications\":true,\"profilePublic\":true,\"showJoinedClubs\":false}},\"tags\":[\"活泼开朗\",\"乐于助人\"],\"phone\":\"139xxxx5678\"}}}}

    // ... 其他用户数据 ...

  ]

}}



请开始生成数据。
"""

        max_iterations = 100  # Adjust as needed, safety break
        
        # --- Stage 2: Generate Users ---
        current_iteration = 0
        while len(all_users) < request.num_users and current_iteration < max_iterations:
            current_iteration += 1
            users_to_request = min(LLM_BATCH_SIZE, request.num_users - len(all_users))

            if users_to_request <= 0:
                break

            existing_users_str = "" # We'll let LLM handle uniqueness within batch and start from 1
            if all_users:
                # Pass existing user IDs and maybe a few other details to help LLM avoid duplicates/generate new ones
                existing_users_str = "\n".join([
                    f"- ID: {u.user_id}, Username: {u.username}, Email: {u.email}"
                    for u in all_users
                ])
                existing_users_str = f"**已有用户数据 (请在此基础上生成新的、不重复的用户):**\n{existing_users_str}\n"
            

            current_prompt_formatted = user_prompt_template.format(
                num_users=users_to_request + 2, # +2 for example discarding
                existing_data_str=existing_users_str
            )
            
            logger.info(f"AI用户数据生成Prompt (Users Iteration {current_iteration}): {current_prompt_formatted[:200]}...")

            messages = [
                Message(role="system", content="你是一个顶尖的数据生成AI，专注于为机器学习任务生成高质量、结构化的模拟用户数据。请严格按照要求的JSON格式返回数据。请确保生成的数据是全新的，并且ID不与提供的已有数据重复。"),
                Message(role="user", content=current_prompt_formatted)
            ]
            
            chat_request = ChatRequest(
                messages=messages,
                model=config.default_model,
                max_tokens=8000,
                temperature=0.7,
                top_p=0.95,
                stream=False
            )

            llm_response_content = ""
            try:
                chat_response = await chat(chat_request)
                llm_response_content = chat_response.response
            except HTTPException as e:
                logger.warning(f"LLM调用失败 (Users Iteration {current_iteration}): {e.detail}")
                continue
            except Exception as e:
                logger.warning(f"LLM调用发生未知错误 (Users Iteration {current_iteration}): {e}")
                continue

            if not llm_response_content.strip():
                logger.warning(f"AI未返回有效的响应内容 (Users Iteration {current_iteration})。")
                continue

            json_string = llm_response_content.strip()
            if json_string.startswith("```json") and json_string.endswith("```"):
                json_string = json_string[len("```json"): -len("```")].strip()
            
            match = re.search(r'"users":\s*\[.*?\]', json_string, re.DOTALL) # More specific regex for users list
            if not match:
                logger.warning(f"AI响应中未找到有效的users JSON结构 (Users Iteration {current_iteration}): {llm_response_content[:200]}...")
                continue
            
            try:
                # Extract only the users array for parsing
                users_array_str = "{\"users\": " + match.group(0).split(':', 1)[1] + "}"
                parsed_response = json.loads(users_array_str)
                users_data = parsed_response.get("users", [])

                existing_user_ids = {u.user_id for u in all_users}
                new_users_batch = []
                for item in users_data:
                    try:
                        # Ensure 'extension' is a dict, not a JSON string
                        if 'extension' in item and isinstance(item['extension'], str):
                            try:
                                item['extension'] = json.loads(item['extension'])
                            except json.JSONDecodeError as json_err:
                                logger.warning(f"Error decoding extension JSON string for user item: {item.get('user_id', 'N/A')}, Error: {json_err}. Original string: {item['extension'][:100]}...")
                                continue # Skip this item if extension is malformed
                            
                        user = UserItem(**item)
                        if user.user_id not in existing_user_ids:
                            new_users_batch.append(user)
                            existing_user_ids.add(user.user_id)
                        else:
                            logger.warning(f"Skipping duplicate user ID: {user.user_id} (Users Iteration {current_iteration})")
                    except Exception as e:
                        logger.warning(f"解析单个用户条目时出错: {item}, 错误: {e} (Users Iteration {current_iteration})")

                all_users.extend(new_users_batch)
                logger.info(f"Users Iteration {current_iteration}: Added {len(new_users_batch)} new users. Total so far: {len(all_users)}")

            except json.JSONDecodeError as e:
                logger.warning(f"AI响应不是有效的JSON (Users Iteration {current_iteration}): {e}, 响应内容: {json_string[:200]}...")
                continue
            except Exception as e:
                logger.warning(f"处理本批次用户数据时出错 (Users Iteration {current_iteration}): {e}")
                continue
        
        if not all_users and request.num_users > 0:
            raise ValueError("未能生成任何有效数据")

       

        # Final truncation to exact requested quantities
        final_users = all_users[:request.num_users]

        if not final_users :
            raise ValueError("未能生成任何有效数据")

        # Save to file
        save_path = None
        if request.save_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name, ext = os.path.splitext(request.save_file)
            file_name = f"{base_name}_{timestamp}{ext}" if ext else f"{base_name}_{timestamp}"
            save_path = os.path.join(current_dir, "generated_data", file_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    for user in final_users:
                        json.dump(user.dict(), f, indent=2, ensure_ascii=False)
                        f.write('\n')
                logger.info(f"用户数据已成功保存到: {save_path}")
            except Exception as e:
                logger.error(f"保存用户数据到文件失败: {e}")
                save_path = None

        return MLDataGenerationResponse(
            users=final_users,
            message=f"成功生成 {len(final_users)} 条用户数据",
            file_path=save_path
        )
            
    except Exception as e:
        logger.error(f"AI机器学习数据生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI机器学习数据生成失败: {e}")


if __name__ == "__main__":
    print(f"启动vLLM代理服务器...")
    print(f"服务器地址: http://{config.server_host}:{config.server_port}")
    print(f"vLLM API地址: {config.vllm_api_url}")
    print(f"默认模型: {config.default_model}")
    print(f"按Ctrl+C可以优雅停机")
    print(f"健康检查: http://{config.server_host}:{config.server_port}/health")
    print(f"聊天接口: http://{config.server_host}:{config.server_port}/chat")
    print(f"简化接口: http://{config.server_host}:{config.server_port}/simple_chat")
    print(f"通义总结接口: http://{config.server_host}:{config.server_port}/summarize_tongyi")
    print(f"生成内容接口: http://{config.server_host}:{config.server_port}/content")
    print(f"社团介绍接口: http://{config.server_host}:{config.server_port}/introduction")
    print(f"社团口号接口: http://{config.server_host}:{config.server_port}/Slogan")
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
    print(f"训练数据生成接口: http://{config.server_host}:{config.server_port}/generate_training_data")
    print(f"机器学习数据生成接口: http://{config.server_host}:{config.server_port}/generate_ml_data")
    print(f"用户数据生成接口: http://{config.server_host}:{config.server_port}/generate_user_data")
    
    # 使用自定义的uvicorn配置类来支持优雅停机
    class UvicornServer(uvicorn.Server):
        def handle_exit(self, sig: int, frame: Optional[Any]) -> None:
            handle_exit_signal(sig, frame)
            return super().handle_exit(sig, frame)

    config = uvicorn.Config(
        app,
        host=config.server_host,
        port=config.server_port,
        log_level=config.log_level.lower(),
        http={'keepalive': 0}  # 禁用 keep-alive
    )
    server = UvicornServer(config=config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("收到键盘中断，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行出错: {e}")
    finally:
        logger.info("服务器已关闭")