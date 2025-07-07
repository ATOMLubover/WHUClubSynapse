#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 服务器测试运行脚本
"""

import sys
import subprocess
import os

def run_mcp_tests():
    """运行 MCP 服务器测试"""
    
    # 设置环境变量
    os.environ['PYTHONPATH'] = os.getcwd()
    
    # 定义测试命令
    test_commands = [
        # 运行所有 MCP 测试
        ["python", "-m", "pytest", "tests/rag/test_mcp_server.py", "-v"],
        
        # 运行特定的测试类别
        ["python", "-m", "pytest", "tests/rag/test_mcp_server.py::test_list_tools", "-v"],
        ["python", "-m", "pytest", "tests/rag/test_mcp_server.py::test_call_tool_retrieve_success", "-v"],
        
        # 运行异步测试
        ["python", "-m", "pytest", "tests/rag/test_mcp_server.py", "-k", "asyncio", "-v"],
        
        # 运行单元测试
        ["python", "-m", "pytest", "tests/rag/test_mcp_server.py", "-k", "not asyncio", "-v"],
    ]
    
    print("开始运行 MCP 服务器测试...")
    print("=" * 60)
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"\n{i}. 运行命令: {' '.join(cmd)}")
        print("-" * 40)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=os.getcwd()
            )
            
            print("STDOUT:")
            print(result.stdout)
            
            if result.stderr:
                print("STDERR:")
                print(result.stderr)
                
            print(f"返回码: {result.returncode}")
            
            if result.returncode != 0:
                print(f"⚠️  命令 {i} 执行失败")
            else:
                print(f"✅ 命令 {i} 执行成功")
                
        except Exception as e:
            print(f"❌ 执行命令时出错: {e}")
        
        print("-" * 40)
    
    print("\n测试运行完成!")
    print("=" * 60)

def check_dependencies():
    """检查测试依赖"""
    required_packages = [
        'pytest',
        'pytest-asyncio', 
        'mcp',
        'chromadb',
        'sentence-transformers',
        'langchain',
        'langchain-community'
    ]
    
    print("检查测试依赖...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 缺失")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n请安装缺失的包: pip install {' '.join(missing_packages)}")
        return False
    
    print("所有依赖都已安装!")
    return True

if __name__ == "__main__":
    print("MCP 服务器测试运行器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 运行测试
    run_mcp_tests()
