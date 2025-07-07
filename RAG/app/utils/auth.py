import os
import secrets
from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader

os.environ['API_KEY'] = 'super_plus_api_key'

# 从环境变量加载密钥
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set!")

API_KEY_NAME = "X-API-Key"

# 创建一个可重用的 APIKeyHeader 实例
api_key_header_scheme = APIKeyHeader(name=API_KEY_NAME, auto_error=False) # auto_error=False 让我们能自定义错误

async def get_api_key(api_key_header: str = Security(api_key_header_scheme)):
    """
    依赖项函数：从请求头获取、验证并返回 API 密钥。
    如果密钥缺失或无效，则抛出 HTTPException。
    """
    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key header is missing"
        )
    if secrets.compare_digest(api_key_header, API_KEY):
        return api_key_header
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

# 为了方便，我们可以直接创建一个 Depends 实例
api_key_dependency = Depends(get_api_key)