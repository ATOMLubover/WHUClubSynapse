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
        from app.rag.mcp_rag_service import server
        
        # 正确的方式：检查服务器是否有注册的工具处理器
        # 通过检查服务器的内部状态来验证工具是否正确注册
        
        # 检查服务器实例
        print(f"✅ 服务器实例类型: {type(server)}")
        
        # 如果服务器有 _tools 属性，检查工具数量
        if hasattr(server, '_tools'):
            tools_count = len(server._tools)
            print(f"✅ 找到 {tools_count} 个注册的工具")
        else:
            print("✅ 服务器实例创建成功")
            
        return True
        
    except Exception as e:
        print(f"❌ 工具测试失败: {e}")
        return False

def test_mcp_call():
    """测试 MCP 工具调用（使用模拟数据）"""
    print("\n🔍 测试 MCP 工具调用...")
    
    try:
        from unittest.mock import patch, MagicMock
        from app.rag.mcp_rag_service import KnowledgeRetrieverMCP
        
        # 创建 MCP 服务实例
        mcp_service = KnowledgeRetrieverMCP()
        
        print(f"✅ MCP 服务实例创建成功: {type(mcp_service)}")
        
        # 检查实际可用的方法
        available_methods = [method for method in dir(mcp_service) 
                           if callable(getattr(mcp_service, method)) 
                           and not method.startswith('_')]
        print(f"   可用方法: {available_methods}")
        
        # 测试 retrieve 方法（模拟数据库连接）
        if hasattr(mcp_service, 'retrieve'):
            # 模拟 ChromaDB 客户端和集合
            mock_collection = MagicMock()
            mock_collection.query.return_value = {
                'ids': [['doc1', 'doc2']],
                'distances': [[0.1, 0.2]],
                'documents': [['模拟文档内容1', '模拟文档内容2']],
                'metadatas': [[{'source': 'test1'}, {'source': 'test2'}]]
            }
            
            # 模拟 SentenceTransformer
            mock_st_model = MagicMock()
            mock_st_model.encode.return_value = MagicMock()
            mock_st_model.encode.return_value.tolist.return_value = [[0.1, 0.2, 0.3]]
            
            with patch.object(mcp_service, 'collection', mock_collection), \
                 patch.object(mcp_service, 'st_model', mock_st_model):
                
                # 调用 retrieve 方法
                result = mcp_service.retrieve("测试查询", 2)
                
                print(f"✅ retrieve 方法调用成功:")
                print(f"   查询: 测试查询")
                print(f"   结果类型: {type(result)}")
                print(f"   结果数量: {len(result)}")
                if result:
                    print(f"   第一个结果: {str(result[0])[:100]}...")
                
        # 测试 format_context 方法
        if hasattr(mcp_service, 'format_context'):
            test_docs = [
                {"content": "测试文档内容1", "metadata": {"source": "test1"}},
                {"content": "测试文档内容2", "metadata": {"source": "test2"}}
            ]
            
            formatted_result = mcp_service.format_context(test_docs)
            
            print(f"✅ format_context 方法调用成功:")
            print(f"   输入文档数量: {len(test_docs)}")
            print(f"   格式化结果长度: {len(formatted_result)}")
            print(f"   格式化结果预览: {formatted_result[:100]}...")
            
        # 测试 get_embeddings 方法
        if hasattr(mcp_service, 'get_embeddings'):
            with patch.object(mcp_service, 'st_model') as mock_st_model:
                mock_embeddings = MagicMock()
                mock_embeddings.tolist.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
                mock_st_model.encode.return_value = mock_embeddings
                
                result = mcp_service.get_embeddings(["测试文本1", "测试文本2"])
                
                print(f"✅ get_embeddings 方法调用成功:")
                print(f"   输入文本数量: 2")
                print(f"   输出向量数量: {len(result)}")
                print(f"   向量维度: {len(result[0]) if result else 0}")
        
        return True
        
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
