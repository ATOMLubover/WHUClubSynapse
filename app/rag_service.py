import torch
import numpy as np
import chromadb
from app.config import settings
from functools import reduce
from transformers import AutoModel, AutoTokenizer
from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 初始化向量数据库客户端
persist_path = settings.VECTOR_DB_PATH
client = chromadb.PersistentClient(path=persist_path)
collection = client.get_or_create_collection(name=settings.VECTRO_DB_COLLECTION)

# 加载模型和分词器
model_dir = settings.EMBEDDING_MODEL_DIR
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModel.from_pretrained(model_dir)

'''
从输入文本获取嵌入向量
'''
def tokenize_inputs(texts: List[str]):
    return tokenizer(texts, return_tensors='pt', padding=True, truncation=True)

def move_to_device(inputs, device):
        return {key: value.to(device) for key, value in inputs.items()}

def get_model_outputs(inputs):
    with torch.no_grad():
        return model(**inputs)

def compute_embeddings(outputs: torch.tensor) -> torch.tensor:  # [batch_size, hidden_size]
    return outputs.last_hidden_state.mean(dim=1)

def get_embeddings(texts: List[str]):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    # 定义流水线步骤
    pipeline = [
        lambda x: tokenize_inputs(x),
        lambda x: move_to_device(x, device),
        lambda x: get_model_outputs(x),
        lambda x: compute_embeddings(x)
    ]
    # 使用流水线。参数的含义分别是：累计值，每个步骤如何处理累计值，处理步骤列表，初始值
    embeddings = reduce(lambda acc, f: f(acc), pipeline, texts)

    return embeddings.cpu().numpy() if isinstance(embeddings, torch.Tensor) else np.array(embeddings)

'''检索最相关的文档片段'''
def retrieve(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    query_embedding = get_embeddings(query if isinstance(query, List) else [query])
    results = collection.query(
        query_embeddings=[query_embedding],
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
    prompt = ChatPromptTemplate.from_template(
        "根据以下上下文（主要）和你的知识（如果上下文不足，再参考），回答问题：\n"
        "{context}\n\n问题：{question}"
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"question": query, "context": context})

'''
rag 全流程
'''
def rag_pipeline(query: str, llm: Any, n_retrieve: int = 3) -> Dict[str: Any]:
    retrieved = retrieve(query, n_retrieve)
    context = format_context(retrieved)
    answer = generate_response(query, context, llm)

    return {
        "answer": answer,
        "source_documents": retrieved,
        "context": context
    }
