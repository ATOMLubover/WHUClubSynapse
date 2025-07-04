#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 MCP 服务器的脚本
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath('.'))

def test_mcp_imports():
    """测试 MCP 相关模块的导入"""
    print("🔍 测试 MCP 模块导入...")
    
    try:
        # 测试基础 MCP 库
        import mcp
        print("✅ mcp 库导入成功")
        
        from mcp.server import Server
        print("✅ mcp.server.Server 导入成功")
        
        from mcp.types import TextContent, Tool, CallToolResult
        print("✅ mcp.types 导入成功")
        
        # 测试项目的 MCP 服务
        from app.rag.mcp_rag_service import server, retriever, KnowledgeRetrieverMCP
        print("✅ MCP 服务器组件导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_mcp_tools():
    """测试 MCP 工具定义"""
    print("\n🔍 测试 MCP 工具定义...")
    
    try:
        import asyncio
        from app.rag.mcp_rag_service import server
        
        async def check_tools():
            list_tools_handler = server.list_tools()
            tools = await list_tools_handler()
            
            print(f"✅ 找到 {len(tools)} 个工具:")
            for tool in tools:
                print(f"   - {tool.name}: {tool.description}")
                
            return tools
        
        tools = asyncio.run(check_tools())
        return len(tools) > 0
        
    except Exception as e:
        print(f"❌ 工具测试失败: {e}")
        return False

def test_mcp_call():
    """测试 MCP 工具调用（使用模拟数据）"""
    print("\n🔍 测试 MCP 工具调用...")
    
    try:
        import asyncio
        import json
        from unittest.mock import patch, MagicMock
        from app.rag.mcp_rag_service import server
        
        async def test_call():
            # 模拟检索器避免真实数据库依赖
            mock_retriever = MagicMock()
            mock_retriever.retrieve.return_value = [
                {"content": "模拟文档内容", "metadata": {"source": "test"}}
            ]
            mock_retriever.format_context.return_value = "格式化的模拟结果"
            
            with patch('app.rag.mcp_rag_service.retriever', mock_retriever):
                call_tool_handler = server.call_tool()
                
                result = await call_tool_handler(
                    name="retrieve",
                    args={
                        "query": "测试查询",
                        "n_results": 1
                    }
                )
                
                response_text = result.content[0].text
                response_data = json.loads(response_text)
                
                print(f"✅ 工具调用成功:")
                print(f"   状态: {response_data['status']}")
                print(f"   查询: {response_data['query']}")
                print(f"   结果类型: {type(response_data['results'])}")
                
                return response_data['status'] == 'success'
        
        success = asyncio.run(test_call())
        return success
        
    except Exception as e:
        print(f"❌ 工具调用测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始快速测试 MCP 服务器")
    print("=" * 50)
    
    tests = [
        ("模块导入", test_mcp_imports),
        ("工具定义", test_mcp_tools), 
        ("工具调用", test_mcp_call),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 测试:")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！MCP 服务器基础功能正常")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置和依赖")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
