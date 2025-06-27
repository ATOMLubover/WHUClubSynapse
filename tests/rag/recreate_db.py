# 在您的初始化脚本或一个单独的工具脚本中
import chromadb
from app.config import settings

client = chromadb.HttpClient(host=settings.CHROMA_SERVER_HOST, port=settings.CHROMA_SERVER_PORT)

# 删除集合
print(f"Deleting collection: {settings.VECTOR_DB_COLLECTION}...")
client.delete_collection(name=settings.VECTOR_DB_COLLECTION)

# 重建集合
print("Recreating collection...")
collection = client.get_or_create_collection(name=settings.VECTOR_DB_COLLECTION)
print("Done.")