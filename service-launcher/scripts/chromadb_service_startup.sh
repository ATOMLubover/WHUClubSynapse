#!/usr/bin/env bash

cd /root/WHUCS-Qwen3

chroma run --host 0.0.0.0 --port 8040 --path /root/autodl-tmp/chroma_db

echo "chromadb started"