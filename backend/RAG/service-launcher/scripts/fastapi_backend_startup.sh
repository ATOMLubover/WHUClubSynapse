#!/usr/bin/env bash

cd /root/WHUCS-Qwen3

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

echo "fastapi backend started"