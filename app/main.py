from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "欢迎使用社团管理系统后端，RAG和AI部分"
    }
