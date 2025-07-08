# 依赖: 此测试假定：
# ChromaDB 服务正在运行，并且可以根据 config.py 中的设置进行连接。
# 嵌入模型存在于 settings.EMBEDDING_MODEL_DIR 指定的目录中。

import pytest
import chromadb
import uuid

from app.rag.mcp_rag_service import retrieve, format_context
from app.configs.config import settings

# ---- 测试数据 ----
# 使用一组固定的示例文档，以便我们可以预测检索结果
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
    这个 fixture 的范围是 "module"，意味着它将在测试模块开始时运行一次，
    并在所有测试结束后运行一次清理代码。
    """
    # 1. 连接到 ChromaDB
    client = chromadb.HttpClient(
        host=settings.CHROMA_SERVER_HOST,
        port=settings.CHROMA_SERVER_PORT
    )

    # 2. 创建一个唯一的临时集合用于测试
    collection_name = f"test-collection-{uuid.uuid4()}"
    collection = client.get_or_create_collection(name=collection_name)

    # 3. 导入 rag_service 中的 get_embeddings 函数，并用它来填充测试数据
    from app.rag.mcp_rag_service import get_embeddings
    embeddings = get_embeddings([doc["content"] for doc in TEST_DOCS])
    
    collection.add(
        ids=[doc["id"] for doc in TEST_DOCS],
        embeddings=embeddings,
        documents=[doc["content"] for doc in TEST_DOCS],
        metadatas=[doc["metadata"] for doc in TEST_DOCS]
    )

    # 4. 将集合对象交给测试函数使用
    yield collection

    # 5. 清理：在所有测试结束后删除临时集合
    client.delete_collection(name=collection_name)


# ---- 功能测试用例 ----

def test_retrieve_normal_query(test_chroma_collection):
    """
    测试 retrieve 函数能否根据查询检索到相关的文档。
    """
    # 替换 rag_service 中的 collection 为我们的测试集合
    from app.rag import mcp_rag_service
    mcp_rag_service.collection = test_chroma_collection

    # 执行检索
    query = "什么是AI？"
    # 检索3个结果，因为我们的过滤器可能会过滤掉一些
    results = retrieve(query, n_results=3)

    # 断言
    assert len(results) > 0, "应该至少检索到一个文档"
    assert any("人工智能" in r["content"] for r in results), "结果中应包含与'人工智能'相关的内容"
    assert "content" in results[0]
    assert "metadata" in results[0]


def test_retrieve_no_relevant_docs(test_chroma_collection):
    """
    测试当查询一个完全不相关的主题时，是否返回空列表或很少的结果。
    这取决于 similarity_threshold 的设置。
    """
    from app.rag import mcp_rag_service
    mcp_rag_service.collection = test_chroma_collection

    query = "法国红酒的历史"
    results = retrieve(query, n_results=5)

    # 由于 EmbeddingsFilter 的存在，不相关的文档应该被过滤掉
    # 注意：这个断言的成功与否，强依赖于 `settings.SIMILARITY_THRESHOLD` 的值
    assert len(results) == 0, "对于完全不相关的主题，不应返回任何文档"


def test_format_context():
    """
    测试 format_context 函数能否正确格式化文档列表。
    """
    test_docs = [
        {"content": "doc1", "metadata": {"source": "s1"}},
        {"content": "doc2", "metadata": {"source": "s2"}}
    ]
    context = format_context(test_docs)
    assert "doc1" in context
    assert "doc2" in context
    assert "文档 1" in context
    assert "文档 2" in context
    assert "Metadata: {'source': 's1'}" in context


def test_format_context_empty_input():
    """
    测试当输入为空列表时，format_context 是否返回空字符串。
    """
    assert format_context([]) == ""
