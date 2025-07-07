import pytest
import asyncio
import json
import subprocess
import tempfile
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from app.utils.singleton import logger

@pytest.mark.asyncio
async def test_mcp_server_integration():
    """
    集成测试：启动真正的MCP服务器并测试通信
    """
    # 启动MCP服务器进程
    project_root = "/root/WHUCS-Qwen3"
    server_script = "/root/WHUCS-Qwen3/app/rag/mcp_rag_service.py"
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "app.rag.mcp_rag_service"],
        cwd=project_root,
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化连接
                await session.initialize()
                
                # 1. 测试列出工具
                tools_result = await session.list_tools()
                tools = tools_result.tools
                
                assert len(tools) > 0, "应该有可用工具"
                logger.debug("可用工具测试成功")
                retrieve_tool = next((tool for tool in tools if tool.name == "retrieve"), None)
                assert retrieve_tool is not None, "应该找到 retrieve 工具"
                logger.debug("retrieve工具测试成功")
                
                # 2. 测试调用工具
                result = await session.call_tool(
                    name="retrieve",
                    arguments={
                        "query": "如何加入一个社团",
                        "n_results": 5
                    }
                )
                
                assert len(result.content) > 0, "应该有返回内容"
                logger.debug("返回测试成功")
                response_text = result.content[0].text
                logger.debug(f"response_text: {response_text}")
                response_data = json.loads(response_text)
                
                # 验证响应结构
                # assert type(response_data) == str
                
    except Exception as e:
        pytest.fail(f"MCP集成测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server_integration())