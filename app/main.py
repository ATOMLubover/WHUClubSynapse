from fastapi import FastAPI
from app.api.endpoints import search, sider_chat
app = FastAPI()

prefix = '/api/v1'
@app.get("/")
def read_root():
    return {
        "message": "欢迎使用社团管理系统后端，RAG和AI部分"
    }

app.include_router(search.router, prefix=prefix, tags=["Search"])
app.include_router(sider_chat.router, prefix=prefix, tags=["SiderChat"])