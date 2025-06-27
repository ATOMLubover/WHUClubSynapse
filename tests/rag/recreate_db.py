# 在您的初始化脚本或一个单独的工具脚本中
import chromadb
from app.config import settings

client = chromadb.HttpClient(host=settings.CHROMA_SERVER_HOST, port=settings.CHROMA_SERVER_PORT)

# 删除集合
print(f"Deleting collection: {settings.CHROMA_RAG_COLLECTION_NAME}...")
client.delete_collection(name=settings.CHROMA_RAG_COLLECTION_NAME)

# 重建集合
print("Recreating collection...")
collection = client.get_or_create_collection(name=settings.CHROMA_RAG_COLLECTION_NAME)
print("Done.")