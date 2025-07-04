#!/bin/bash

# 启动推荐服务
echo "Starting recommendation service..."
cd recommend_system
python recommend_server.py &
RECOMMEND_PID=$!

# 等待推荐服务启动
sleep 5

# 启动主服务
echo "Starting main service..."
cd ../AIserver
python vllm_proxy_server.py &
MAIN_PID=$!

# 等待信号处理
trap "kill $RECOMMEND_PID $MAIN_PID; exit" SIGINT SIGTERM

# 保持脚本运行
wait 