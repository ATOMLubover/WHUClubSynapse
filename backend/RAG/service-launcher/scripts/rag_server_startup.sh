cd /root/WHUCS-Qwen3

uvicorn app.api.endpoints.internal_rag_service:app --host 0.0.0.0 --port 8020 --reload

echo "rag server started"