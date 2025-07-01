#!/usr/bin/env bash

# Qwen3-8B 的默认 max-model-len 是 32768，不用担心不够用

python -m vllm.entrypoints.openai.api_server \
--model "/root/autodl-tmp/Qwen/Qwen3-8B-AWQ" \
--served-model-name "Qwen3-8B-AWQ" \
--max-model-len 8192 \
--trust-remote-code \
--port 8010 \
--quantization awq