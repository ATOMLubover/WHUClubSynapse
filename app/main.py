from fastapi import FastAPI
from app.api.endpoints import search
app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "欢迎使用社团管理系统后端，RAG和AI部分"
    }

app.include_router(search.router, prefix='/api/v1', tags=["Search"])