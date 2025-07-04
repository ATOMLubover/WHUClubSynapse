import asyncio
import json
from typing import List, Dict, Any, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool, CallToolRequest, CallToolResult
import mcp.server.stdio

import chromadb
from sentence_transformers import SentenceTransformer

from app.configs.config import settings
from app.utils.singleton import logger
from langchain.retrievers.document_compressors import DocumentCompressorPipeline, EmbeddingsFilter
from langchain_community.document_transformers import LongContextReorder
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

class KnowledgeRetrieverMCP:
    def __init__(self):
        # 初始化向量数据库客户端
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_SERVER_HOST,
            port=settings.CHROMA_SERVER_PORT
        )
        self.collection = self.client.get_or_create_collection(name=settings.CHROMA_RAG_COLLECTION_NAME)

        # 加载模型
        self.st_model = SentenceTransformer(settings.EMBEDDING_MODEL_DIR)
        self.lc_embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_DIR,
            model_kwargs={
                'device': 'cpu'
            }
        )
        self.lc_reorder = LongContextReorder()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        对文本进行向量化
        参数:
        texts: 文本列表
        返回值:
        一个Python的向量列表。
        """
        embeddings = self.st_model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def retrieve(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        '''
        检索最相关的文档片段，包含 长上下文重排 和 上下文压缩 优化
        query: 用于查询相关文档的输入
        n_results: 决定取前几个最相关的文档
        '''
        try:
            query_embedding = self.get_embeddings(query if isinstance(query, List) else [query])
            retrieved_docs = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["metadatas", "documents", "distances"]
            )

            docs = []
            if not retrieved_docs['ids'] or not retrieved_docs['ids'][0]:
                return []
    
            for i in range(len(retrieved_docs["ids"][0])):
                similarity = 1 - retrieved_docs['distances'][0][i]
                metadata=retrieved_docs["metadatas"][0][i]
                metadata['similarity_score'] = similarity
        
                docs.append(
                    Document(
                        page_content=retrieved_docs["documents"][0][i],
                        metadata=metadata
                    )
                )
    
            embeddings_filter = EmbeddingsFilter(
                embeddings=self.lc_embeddings,
                similarity_threshold=settings.SIMILARITY_THRESHOLD
            )
            # 压缩管道，包含 长上下文重排 和 上下文压缩
            pipeline_compressor = DocumentCompressorPipeline(
                transformers=[embeddings_filter, self.lc_reorder]
            )

            compressed_docs = pipeline_compressor.compress_documents(docs, query)

            results = [
                {"content": doc.page_content, "metadata": doc.metadata}
                for doc in compressed_docs
            ]

            for i, result in enumerate(results):
                logger.debug(f"""第{i+1}篇文档，前30个字符为'{result['content'][:30]}'，
                            与prompt的相似度为{result['metadata']['similarity_score']}""")

            return results
    
        except Exception as e:
            logger.error(f"检索过程中发生错误: {str(e)}")
            return []


    def format_context(self, retrieved_docs: List[Dict]) -> str:
        '''
        格式化检索结果为 LLM 输入
        参数:
        retrieved_docs: 检索到的文档
        '''
        return "\n\n".join(
            f"""
            文档 {i + 1}:\n{doc['content']}\nMetadata: {doc['metadata']}
            """ for i, doc in enumerate(retrieved_docs)
        )

# 创建 MCP 服务器实例
server = Server("knowledge-retriever")
retriever = KnowledgeRetrieverMCP()

# 这个服务器提供的工具列表
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    返回可用的工具列表
    """
    return [
        Tool(
            name="retrieve",
            description="从知识库中检索与查询最相关的文档片段",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "查询文本"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "返回的文档数量",
                        "default": 5,
                        "minimum": 0,
                        "maximum": 10 
                    }
                },
                "required": ["query"]
            }
        )
    ]

# 处理工具调用，其实相当于调用函数
@server.call_tool()
async def handle_call_tool(name: str, args: Dict[str, Any]) -> CallToolResult:
    """
    处理工具调用请求
    """
    if name != "retrieve":
        raise ValueError(f"未知工具: {name}")
    
    try:
        query = args.get('query')
        n_results = args.get('n_results', 5) 
        if not query:
            raise ValueError("query 参数不能为空")
        retrieved_docs = retriever.retrieve(query, n_results)
        results = retriever.format_context(retrieved_docs)
        
        response = {
            "status": "success",
            "query": query,
            "results": results,
            "total": len(retrieved_docs)
        }

        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(response, ensure_ascii=False, indent=2)
                )
            ]
        )
    except Exception as e:
        logger.error(f"工具调用失败: {str(e)}")
        error_response = {
            "status": "error",
            "message": str(e),
            "results": ""
        }

        return CallToolResult(
            content=[
                TextContent(
                    type="text", 
                    text=json.dumps(error_response, ensure_ascii=False)
                )
            ]
        )

     

# 主函数，启动服务器，运行 MCP 服务
async def main():
    # 运行 MCP 服务器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream=read_stream,
            write_stream=write_stream,
            InitializationOptions=InitializationOptions(
                server_name="knowledge-retriever",
                server_version="1.0.1",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ) 
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())