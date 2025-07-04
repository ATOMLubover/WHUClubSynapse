# 测试 MCP 服务器的 MCP 接口
# 依赖: 此测试假定：
# ChromaDB 服务正在运行，并且可以根据 config.py 中的设置进行连接。
# 嵌入模型存在于 settings.EMBEDDING_MODEL_DIR 指定的目录中。

import pytest
import asyncio
import json
import uuid
import chromadb
from unittest.mock import patch, AsyncMock

from mcp.types import TextContent, Tool, CallToolResult
from app.rag.mcp_rag_service import server, retriever, KnowledgeRetrieverMCP
from app.configs.config import settings

# ---- 测试数据 ----
TEST_DOCS = [
    {"id": "doc1", "content": "人工智能是计算机科学的一个分支。", "metadata": {"source": "wiki-ai"}},
    {"id": "doc2", "content": "机器学习是实现人工智能的一种方法。", "metadata": {"source": "wiki-ml"}},
    {"id": "doc3", "content": "深度学习是机器学习的一个热门领域。", "metadata": {"source": "wiki-dl"}},
    {"id": "doc4", "content": "自然语言处理专注于计算机与人类语言的交互。", "metadata": {"source": "wiki-nlp"}},
    {"id": "doc5", "content": "北京是中国的首都，也是一座历史悠久的文化名城。", "metadata": {"source": "geo-beijing"}},
]

# ---- Fixtures ----

@pytest.fixture(scope="module")
def test_chroma_collection():
    """
    创建一个用于测试的 ChromaDB 集合，并在测试结束后清理。
    """
    # 1. 连接到 ChromaDB
    client = chromadb.HttpClient(
        host=settings.CHROMA_SERVER_HOST,
        port=settings.CHROMA_SERVER_PORT
    )

    # 2. 创建一个唯一的临时集合用于测试
    collection_name = f"test-mcp-collection-{uuid.uuid4()}"
    collection = client.get_or_create_collection(name=collection_name)

    # 3. 创建测试用的检索器实例并填充测试数据
    test_retriever = KnowledgeRetrieverMCP()
    embeddings = test_retriever.get_embeddings([doc["content"] for doc in TEST_DOCS])
    
    collection.add(
        ids=[doc["id"] for doc in TEST_DOCS],
        embeddings=embeddings,
        documents=[doc["content"] for doc in TEST_DOCS],
        metadatas=[doc["metadata"] for doc in TEST_DOCS]
    )

    # 4. 将集合对象交给测试函数使用
    yield collection, test_retriever

    # 5. 清理：在所有测试结束后删除临时集合
    client.delete_collection(name=collection_name)

@pytest.fixture
def mock_retriever(test_chroma_collection):
    """
    创建一个模拟的检索器，使用测试集合
    """
    collection, test_retriever = test_chroma_collection
    # 替换全局检索器的集合为测试集合
    test_retriever.collection = collection
    return test_retriever

# ---- MCP 服务器接口测试 ----

@pytest.mark.asyncio
async def test_list_tools():
    """
    测试 MCP 服务器能否正确返回可用的工具列表
    """
    tools = await server.list_tools()()
    
    assert isinstance(tools, list), "工具列表应该是一个list"
    assert len(tools) > 0, "至少应该有一个工具"
    
    # 检查 retrieve 工具是否存在
    retrieve_tool = next((tool for tool in tools if tool.name == "retrieve"), None)
    assert retrieve_tool is not None, "应该包含 'retrieve' 工具"
    assert retrieve_tool.description is not None, "工具应该有描述"
    assert retrieve_tool.inputSchema is not None, "工具应该有输入schema"
    
    # 检查 schema 结构
    schema = retrieve_tool.inputSchema
    assert schema["type"] == "object", "schema 类型应该是 object"
    assert "properties" in schema, "schema 应该包含 properties"
    assert "query" in schema["properties"], "应该包含 query 参数"
    assert "n_results" in schema["properties"], "应该包含 n_results 参数"
    assert "required" in schema, "schema 应该包含 required 字段"
    assert "query" in schema["required"], "query 应该是必需参数"

@pytest.mark.asyncio
async def test_call_tool_retrieve_success(mock_retriever):
    """
    测试成功调用 retrieve 工具
    """
    # 模拟替换全局检索器
    with patch('app.rag.mcp_rag_service.retriever', mock_retriever):
        # 调用工具
        result = await server.call_tool()(
            name="retrieve",
            args={
                "query": "什么是人工智能？",
                "n_results": 3
            }
        )
        
        assert isinstance(result, CallToolResult), "返回结果应该是 CallToolResult 类型"
        assert len(result.content) > 0, "应该有返回内容"
        assert isinstance(result.content[0], TextContent), "内容应该是 TextContent 类型"
        
        # 解析返回的 JSON
        response_text = result.content[0].text
        response_data = json.loads(response_text)
        assert response_data["status"] == "success", "状态应该是 success"
        assert "query" in response_data, "应该包含查询信息"
        assert "results" in response_data, "应该包含结果"
        assert "total" in response_data, "应该包含总数"
        assert response_data["query"] == "什么是人工智能？", "查询应该匹配"
        # total 是格式化结果字符串的长度，不是文档数量
        assert isinstance(response_data["total"], int), "总数应该是整数"

@pytest.mark.asyncio
async def test_call_tool_retrieve_with_results(mock_retriever):
    """
    测试检索到相关文档的情况
    """
    with patch('app.rag.mcp_rag_service.retriever', mock_retriever):
        result = await server.call_tool()(
            name="retrieve", 
            args={
                "query": "人工智能",
                "n_results": 2
            }
        )
        
        response_text = result.content[0].text
        response_data = json.loads(response_text)
        
        assert response_data["status"] == "success"
        # 检查格式化后的结果字符串
        assert isinstance(response_data["results"], str), "结果应该是格式化的字符串"
        assert "文档" in response_data["results"], "结果应该包含文档标识"

@pytest.mark.asyncio
async def test_call_tool_retrieve_empty_query():
    """
    测试空查询的错误处理
    """
    result = await server.call_tool()(
        name="retrieve",
        args={
            "query": "",
            "n_results": 5
        }
    )
    
    response_text = result.content[0].text
    response_data = json.loads(response_text)
    
    assert response_data["status"] == "error", "状态应该是 error"
    assert "message" in response_data, "应该包含错误信息"
    assert response_data["results"] == "", "错误时结果应该为空字符串"

@pytest.mark.asyncio
async def test_call_tool_retrieve_missing_query():
    """
    测试缺少必需参数的错误处理
    """
    result = await server.call_tool()(
        name="retrieve",
        args={
            "n_results": 5
            # 缺少 query 参数
        }
    )
    
    response_text = result.content[0].text
    response_data = json.loads(response_text)
    
    assert response_data["status"] == "error", "状态应该是 error"
    assert "query 参数不能为空" in response_data["message"], "应该提示缺少 query 参数"

@pytest.mark.asyncio
async def test_call_tool_retrieve_default_n_results(mock_retriever):
    """
    测试 n_results 参数的默认值
    """
    with patch('app.rag.mcp_rag_service.retriever', mock_retriever):
        result = await server.call_tool()(
            name="retrieve",
            args={
                "query": "机器学习"
                # 不提供 n_results，应该使用默认值 5
            }
        )
        
        response_text = result.content[0].text
        response_data = json.loads(response_text)
        
        assert response_data["status"] == "success"
        # 验证确实使用了默认参数（通过检查调用是否成功）

@pytest.mark.asyncio
async def test_call_tool_unknown_tool():
    """
    测试调用未知工具的错误处理
    """
    with pytest.raises(ValueError, match="未知工具"):
        await server.call_tool()(
            name="unknown_tool",
            args={"query": "test"}
        )

@pytest.mark.asyncio
async def test_call_tool_retrieve_database_error():
    """
    测试数据库连接错误的处理
    """
    # 模拟数据库错误
    mock_error_retriever = AsyncMock()
    mock_error_retriever.retrieve.side_effect = Exception("数据库连接失败")
    mock_error_retriever.format_context.return_value = ""
    
    with patch('app.rag.mcp_rag_service.retriever', mock_error_retriever):
        result = await server.call_tool()(
            name="retrieve",
            args={
                "query": "测试查询",
                "n_results": 3
            }
        )
        
        response_text = result.content[0].text
        response_data = json.loads(response_text)
        
        assert response_data["status"] == "error"
        assert "message" in response_data

# ---- KnowledgeRetrieverMCP 类测试 ----

def test_knowledge_retriever_init():
    """
    测试 KnowledgeRetrieverMCP 类的初始化
    """
    retriever_instance = KnowledgeRetrieverMCP()
    
    assert retriever_instance.client is not None, "ChromaDB 客户端应该被初始化"
    assert retriever_instance.collection is not None, "集合应该被初始化"
    assert retriever_instance.st_model is not None, "SentenceTransformer 模型应该被初始化"
    assert retriever_instance.lc_embeddings is not None, "LangChain embeddings 应该被初始化"
    assert retriever_instance.lc_reorder is not None, "长上下文重排序器应该被初始化"

def test_get_embeddings():
    """
    测试向量化功能
    """
    retriever_instance = KnowledgeRetrieverMCP()
    
    texts = ["这是测试文本", "另一个测试文本"]
    embeddings = retriever_instance.get_embeddings(texts)
    
    assert isinstance(embeddings, list), "应该返回列表"
    assert len(embeddings) == len(texts), "向量数量应该与文本数量一致"
    assert all(isinstance(emb, list) for emb in embeddings), "每个向量应该是列表"
    assert all(len(emb) > 0 for emb in embeddings), "向量不应该为空"

def test_retrieve_with_test_collection(mock_retriever):
    """
    测试检索功能
    """
    query = "人工智能"
    results = mock_retriever.retrieve(query, n_results=3)
    
    assert isinstance(results, list), "应该返回列表"
    # 根据相似度过滤，可能返回空列表或有结果
    for result in results:
        assert "content" in result, "每个结果应该包含 content"
        assert "metadata" in result, "每个结果应该包含 metadata"

def test_format_context():
    """
    测试上下文格式化功能
    """
    retriever_instance = KnowledgeRetrieverMCP()
    
    test_docs = [
        {"content": "文档1内容", "metadata": {"source": "test1"}},
        {"content": "文档2内容", "metadata": {"source": "test2"}}
    ]
    
    formatted = retriever_instance.format_context(test_docs)
    
    assert isinstance(formatted, str), "应该返回字符串"
    assert "文档 1" in formatted, "应该包含文档编号"
    assert "文档 2" in formatted, "应该包含文档编号"
    assert "文档1内容" in formatted, "应该包含文档内容"
    assert "文档2内容" in formatted, "应该包含文档内容"
    assert "test1" in formatted, "应该包含元数据"

def test_format_context_empty():
    """
    测试空文档列表的格式化
    """
    retriever_instance = KnowledgeRetrieverMCP()
    
    formatted = retriever_instance.format_context([])
    
    assert formatted == "", "空列表应该返回空字符串"

# ---- 集成测试 ----

@pytest.mark.asyncio
async def test_end_to_end_mcp_workflow(mock_retriever):
    """
    端到端测试：从列出工具到调用工具的完整流程
    """
    # 1. 列出工具
    tools = await server.list_tools()()
    assert len(tools) > 0, "应该有可用工具"
    
    # 2. 找到 retrieve 工具
    retrieve_tool = next((tool for tool in tools if tool.name == "retrieve"), None)
    assert retrieve_tool is not None, "应该找到 retrieve 工具"
    
    # 3. 调用工具
    with patch('app.rag.mcp_rag_service.retriever', mock_retriever):
        result = await server.call_tool()(
            name="retrieve",
            args={
                "query": "深度学习相关内容",
                "n_results": 2
            }
        )
        
        # 4. 验证结果
        assert isinstance(result, CallToolResult), "应该返回 CallToolResult"
        response_text = result.content[0].text
        response_data = json.loads(response_text)
        assert response_data["status"] == "success", "调用应该成功"

if __name__ == "__main__":
    # 运行测试的示例
    # pytest tests/rag/test_mcp_server.py -v
    pass
