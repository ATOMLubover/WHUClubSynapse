import chromadb
from app.config import settings
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import SentenceTransformer

# 初始化向量数据库客户端
client = chromadb.HttpClient(
    host=settings.CHROMA_SERVER_HOST,
    port=settings.CHROMA_SERVER_PORT
)
collection = client.get_or_create_collection(name=settings.CHROMA_RAG_COLLECTION_NAME)

# 加载模型
st_model = SentenceTransformer(settings.EMBEDDING_MODEL_DIR)

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    接收一个文本列表，使用已加载的 st_model 进行向量化，
    并返回一个Python的向量列表。
    """
    embeddings = st_model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()

'''检索最相关的文档片段'''
def retrieve(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    query_embedding = get_embeddings(query if isinstance(query, List) else [query])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    return [
        {"content": doc, "metadata": meta}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]

'''格式化检索结果为 LLM 输入'''
def format_context(retrieved_docs: List[Dict]) -> str:
    return "\n\n".join(
        f"""
        文档 {i+1}:\n{doc['content']}\nMetadata: {doc['metadata']}
        """for i, doc in enumerate(retrieved_docs)
    )

'''生成最终回答'''
def generate_response(query: str, context: str, llm: Any) -> str:
    prompt_template = ChatPromptTemplate.from_template(
        "根据以下上下文（主要）和你的知识（如果上下文不足，再参考），回答问题：\n{context}\n\n问题：{question}"
    )
    prompt = prompt_template.format(context=context, question=query)

    chain = llm | StrOutputParser()
    return chain.invoke(prompt)

'''
rag 全流程
'''
def rag_pipeline(query: str, llm: Any, n_retrieve: int = 3) -> Dict[str, Any]:
    retrieved = retrieve(query, n_retrieve)
    context = format_context(retrieved)
    answer = generate_response(query, context, llm)

    return {
        "answer": answer,
        "source_documents": retrieved,
        "context": context
    }
