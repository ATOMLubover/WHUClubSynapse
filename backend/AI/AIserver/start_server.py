#!/usr/bin/env python3
"""
vLLM代理服务器启动脚本
"""

import sys
import os
import subprocess
import time
import requests
import json

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

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'requests',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少必要的依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n请运行以下命令安装依赖:")
        print("pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_vllm_server():
    """检查vLLM服务器是否可访问"""
    try:
        health_url = config.vllm_api_url.replace("/v1/chat/completions", "/health")
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            print("✅ vLLM服务器连接正常")
            return True
        else:
            print(f"⚠️  vLLM服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到vLLM服务器")
        print(f"   请确保vLLM服务器正在运行: {config.vllm_api_url}")
        return False
    except Exception as e:
        print(f"⚠️  检查vLLM服务器时发生错误: {e}")
        return False

def ensure_financial_data_file():
    """确保财务数据文件存在，如果不存在则创建空文件"""
    data_file_path = os.path.join(current_dir, config.financial_data_file)
    if not os.path.exists(data_file_path):
        try:
            with open(data_file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f) # 写入一个空的JSON对象，适应多社团结构
            print(f"✅ 财务数据文件已创建: {data_file_path}")
        except Exception as e:
            print(f"❌ 创建财务数据文件失败: {e}")
            sys.exit(1)
    else:
        print(f"✅ 财务数据文件已存在: {data_file_path}")

def ensure_club_information_file():
    """确保社团信息文件存在，如果不存在则创建空文件"""
    club_info_file_path = os.path.join(current_dir, config.club_information_file) if hasattr(config, 'club_information_file') else os.path.join(current_dir, 'Club_information.json')
    if not os.path.exists(club_info_file_path):
        try:
            with open(club_info_file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f) # 写入一个空的JSON对象
            print(f"✅ 社团信息文件已创建: {club_info_file_path}")
        except Exception as e:
            print(f"❌ 创建社团信息文件失败: {e}")
            sys.exit(1)
    else:
        print(f"✅ 社团信息文件已存在: {club_info_file_path}")

def print_server_info():
    """打印服务器信息"""
    print("\n" + "="*60)
    print("🚀 vLLM代理服务器配置信息")
    print("="*60)
    print(f"服务器地址: http://{config.server_host}:{config.server_port}")
    print(f"vLLM API地址: {config.vllm_api_url}")
    print(f"默认模型: {config.default_model}")
    print(f"请求超时: {config.request_timeout}秒")
    print(f"日志级别: {config.log_level}")
    print(f"财务数据文件: {os.path.join(current_dir, config.financial_data_file)}")
    print(f"社团信息文件: {os.path.join(current_dir, config.club_information_file) if hasattr(config, 'club_information_file') else os.path.join(current_dir, 'Club_information.json')}")
    print("="*60)

def print_api_endpoints():
    """打印API端点信息"""
    print("\n📋 可用的API端点:")
    print(f"   GET  /                    - 服务器状态")
    print(f"   GET  /health              - 健康检查")
    print(f"   POST /chat                - 完整聊天接口")
    print(f"   POST /simple_chat         - 简化聊天接口")
    print(f"   GET  /models              - 模型列表")
    print(f"   GET  /config              - 配置信息")
    print(f"   POST /introduction - 社团介绍生成接口")
    print(f"   POST /Slogan     - 社团口号生成接口")
    print(f"   GET  /reload_config       - 配置重载接口")
    print(f"   POST /screen_application  - 智能申请筛选助手接口")
    print(f"   POST /club_atmosphere      - 社团\"氛围\"透视镜接口")
    print(f"   POST /plan_event           - 智能活动策划参谋接口")
    print(f"   POST /club_recommend       - 社团推荐接口")
    print(f"   POST /update_club_data     - 更新社团信息接口")
    print(f"   GET  /docs                - API文档 (Swagger UI)")
    print(f"   GET  /redoc               - API文档 (ReDoc)")

def start_server():
    """启动服务器"""
    print("\n🔄 正在启动vLLM代理服务器...")
    
    try:
        # 导入并运行服务器
        from vllm_proxy_server import app
        import uvicorn
        
        print(f"✅ 服务器启动成功!")
        print(f"🌐 访问地址: http://{config.server_host}:{config.server_port}")
        print(f"📖 API文档: http://{config.server_host}:{config.server_port}/docs")
        print("\n按 Ctrl+C 停止服务器")
        
        uvicorn.run(
            app,
            host=config.server_host,
            port=config.server_port,
            log_level=config.log_level.lower()
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动服务器时发生错误: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("🎯 vLLM代理服务器启动器")
    print("="*40)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 确保财务数据文件存在
    ensure_financial_data_file()
    
    # 确保社团信息文件存在
    ensure_club_information_file()
    
    # 检查vLLM服务器
    print("\n🔍 检查vLLM服务器连接...")
    vllm_available = check_vllm_server()
    
    # 打印服务器信息
    print_server_info()
    
    # 打印API端点
    print_api_endpoints()
    
    if not vllm_available:
        print("\n⚠️  警告: vLLM服务器不可用")
        print("   服务器仍将启动，但聊天功能可能无法正常工作")
        print("   请确保vLLM服务器正在运行后再使用聊天功能")
        
        response = input("\n是否继续启动服务器? (y/N): ")
        if response.lower() != 'y':
            print("启动已取消")
            sys.exit(0)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main() 