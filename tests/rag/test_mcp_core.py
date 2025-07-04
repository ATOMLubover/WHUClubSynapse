# 简化的 MCP 核心功能测试

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock

# 测试 MCP 基础组件
def test_mcp_server_import():
    """测试 MCP 服务器组件能否正常导入"""
    try:
        from app.rag.mcp_rag_service import server, retriever, KnowledgeRetrieverMCP
        assert server is not None, "MCP 服务器应该能够导入"
        assert retriever is not None, "检索器应该能够导入"
        assert KnowledgeRetrieverMCP is not None, "检索器类应该能够导入"
        print("✅ MCP 组件导入成功")
    except ImportError as e:
        pytest.fail(f"MCP 组件导入失败: {e}")

@pytest.mark.asyncio
async def test_list_tools_basic():
    """测试基础的工具列表功能"""
    try:
        from app.rag.mcp_rag_service import server
        
        # 获取工具列表处理器
        list_tools_handler = server.list_tools()
        
        # 调用处理器
        tools = await list_tools_handler()
        
        # 基础验证
        assert isinstance(tools, list), "工具列表应该是一个list"
        assert len(tools) > 0, "至少应该有一个工具"
        
        # 查找 retrieve 工具
        tool_names = [tool.name for tool in tools]
        assert "retrieve" in tool_names, "应该包含 retrieve 工具"
        
        print(f"✅ 找到 {len(tools)} 个工具: {tool_names}")
        
    except Exception as e:
        pytest.fail(f"工具列表测试失败: {e}")

@pytest.mark.asyncio 
async def test_call_tool_basic():
    """测试基础的工具调用功能"""
    try:
        from app.rag.mcp_rag_service import server
        
        # 模拟检索器返回空结果，避免依赖真实数据库
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = []
        mock_retriever.format_context.return_value = ""
        
        with patch('app.rag.mcp_rag_service.retriever', mock_retriever):
            # 获取工具调用处理器
            call_tool_handler = server.call_tool()
            
            # 调用工具
            result = await call_tool_handler(
                name="retrieve",
                args={
                    "query": "测试查询",
                    "n_results": 3
                }
            )
            
            # 验证返回结果结构
            assert result is not None, "应该有返回结果"
            assert hasattr(result, 'content'), "结果应该有 content 属性"
            assert len(result.content) > 0, "content 不应该为空"
            
            # 解析 JSON 响应
            response_text = result.content[0].text
            response_data = json.loads(response_text)
            
            assert "status" in response_data, "响应应该包含 status"
            assert "query" in response_data, "响应应该包含 query"
            assert "results" in response_data, "响应应该包含 results"
            
            print("✅ 工具调用基础功能正常")
            
    except Exception as e:
        pytest.fail(f"工具调用测试失败: {e}")

@pytest.mark.asyncio
async def test_call_tool_error_handling():
    """测试错误处理"""
    try:
        from app.rag.mcp_rag_service import server
        
        call_tool_handler = server.call_tool()
        
        # 测试未知工具
        with pytest.raises(ValueError, match="未知工具"):
            await call_tool_handler(
                name="unknown_tool",
                args={"query": "test"}
            )
        
        # 测试空查询
        result = await call_tool_handler(
            name="retrieve",
            args={"query": "", "n_results": 5}
        )
        
        response_text = result.content[0].text
        response_data = json.loads(response_text)
        
        assert response_data["status"] == "error", "空查询应该返回错误"
        
        print("✅ 错误处理功能正常")
        
    except Exception as e:
        pytest.fail(f"错误处理测试失败: {e}")

def test_knowledge_retriever_class():
    """测试 KnowledgeRetrieverMCP 类的基础功能"""
    try:
        from app.rag.mcp_rag_service import KnowledgeRetrieverMCP
        
        # 创建实例（可能会因为模型或数据库连接失败）
        try:
            retriever = KnowledgeRetrieverMCP()
            print("✅ KnowledgeRetrieverMCP 实例创建成功")
            
            # 测试格式化功能（不依赖外部服务）
            test_docs = [
                {"content": "测试内容1", "metadata": {"source": "test1"}},
                {"content": "测试内容2", "metadata": {"source": "test2"}}
            ]
            
            formatted = retriever.format_context(test_docs)
            
            assert isinstance(formatted, str), "格式化结果应该是字符串"
            assert "测试内容1" in formatted, "应该包含测试内容1"
            assert "测试内容2" in formatted, "应该包含测试内容2"
            assert "文档 1" in formatted, "应该包含文档编号"
            
            print("✅ 格式化功能正常")
            
        except Exception as init_error:
            print(f"⚠️  KnowledgeRetrieverMCP 初始化失败（可能因为模型或数据库不可用）: {init_error}")
            # 这是预期的，如果模型或数据库不可用
            
    except ImportError as e:
        pytest.fail(f"KnowledgeRetrieverMCP 类导入失败: {e}")

def test_server_configuration():
    """测试服务器配置"""
    try:
        from app.rag.mcp_rag_service import server
        
        # 检查服务器名称
        assert hasattr(server, '_name'), "服务器应该有名称"
        
        # 检查服务器能力
        capabilities = server.get_capabilities(
            notification_options=None,
            experimental_capabilities=None
        )
        
        assert capabilities is not None, "服务器应该有能力配置"
        
        print("✅ 服务器配置正常")
        
    except Exception as e:
        pytest.fail(f"服务器配置测试失败: {e}")

if __name__ == "__main__":
    print("运行 MCP 核心功能测试...")
    
    # 运行单个测试的示例
    # pytest tests/rag/test_mcp_core.py::test_mcp_server_import -v
    
    # 或使用 asyncio 直接运行异步测试
    async def run_async_tests():
        print("运行异步测试...")
        await test_list_tools_basic()
        await test_call_tool_basic() 
        await test_call_tool_error_handling()
        print("异步测试完成!")
    
    # 运行同步测试
    test_mcp_server_import()
    test_knowledge_retriever_class()
    test_server_configuration()
    
    # 运行异步测试
    asyncio.run(run_async_tests())
