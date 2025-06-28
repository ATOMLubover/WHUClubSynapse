from modelscope import snapshot_download

# model_dir = snapshot_download('Qwen/Qwen3-8B', cache_dir='/root/autodl-tmp', revision='master')
embedding_dir = snapshot_download('AI-ModelScope/m3e-base', cache_dir='/root/autodl-tmp', revision='master')
