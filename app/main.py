from fastapi import FastAPI, Security, HTTPException, status
from app.api.endpoints import search, sider_chat
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

app = FastAPI(dependencies=[Depends])

origins = [
    "http://localhost",
    # 如果不确定，为了测试可以暂时使用"*"，但生产环境请务必指定具体域名
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # 允许所有HTTP方法
    allow_headers=["*"], # 允许所有HTTP头
)

prefix = '/api/v1'
@app.get("/")
def read_root():
    return {
        "message": "欢迎使用社团管理系统后端，RAG和AI部分"
    }

app.include_router(search.router, prefix=prefix, tags=["Search"])
app.include_router(sider_chat.router, prefix=prefix, tags=["SiderChat"])