#!/usr/bin/env python3
"""
测试config_manager模块导入
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print("当前工作目录:", os.getcwd())
print("Python路径:", sys.path[:3])  # 只显示前3个路径

try:
    from config_manager import config
    print("✅ 成功导入config_manager模块")
    print(f"服务器地址: {config.server_host}:{config.server_port}")
    print(f"vLLM API地址: {config.vllm_api_url}")
    print(f"默认模型: {config.default_model}")
    print(f"请求超时: {config.request_timeout}秒")
    print(f"日志级别: {config.log_level}")
except ImportError as e:
    print(f"❌ 导入config_manager模块失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 其他错误: {e}")
    sys.exit(1)

print("✅ 所有配置项导入成功！") 