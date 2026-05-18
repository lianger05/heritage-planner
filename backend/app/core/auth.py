"""API Key 简易认证中间件

使用 X-API-Key 请求头进行身份验证。
写操作（POST/PUT/DELETE）强制校验，读操作（GET/OPTIONS）可选跳过。
若未配置 API_KEY 环境变量，则跳过所有认证（向后兼容开发环境）。
"""

import os
import logging

from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

# 受保护的 HTTP 方法：需要 API Key
_PROTECTED_METHODS = {"POST", "PUT", "DELETE", "PATCH"}

# 公开端点路径前缀：即使 POST 方法也豁免认证
_PUBLIC_PATH_PREFIXES = (
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
)


def _get_api_key() -> str | None:
    """获取配置的 API Key，未配置返回 None"""
    return os.getenv("API_KEY") or None


async def api_key_middleware(request: Request, call_next):
    """API Key 认证中间件"""
    api_key = _get_api_key()

    # 未配置 API_KEY → 跳过认证（开发/测试环境）
    if not api_key:
        return await call_next(request)

    # 公开文档路径 → 豁免认证
    if request.url.path.startswith(_PUBLIC_PATH_PREFIXES):
        return await call_next(request)

    # 读操作 → 豁免认证
    if request.method not in _PROTECTED_METHODS:
        return await call_next(request)

    # 写操作 → 强制校验
    client_key = request.headers.get("X-API-Key")
    if not client_key:
        logger.warning("Missing X-API-Key header on %s %s", request.method, request.url.path)
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header. 请在请求头中提供有效的 API Key。",
        )

    if client_key != api_key:
        logger.warning("Invalid X-API-Key on %s %s", request.method, request.url.path)
        raise HTTPException(
            status_code=401,
            detail="Invalid API key. 提供的 API Key 无效。",
        )

    return await call_next(request)
