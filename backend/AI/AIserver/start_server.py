#!/usr/bin/env python3
"""
vLLM代理服务器启动脚本
"""

import sys
import os
import subprocess
import time
import requests

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
    print(f"   POST /generate/introduction - 社团介绍生成接口")
    print(f"   POST /generate/Slogan     - 社团口号生成接口")
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