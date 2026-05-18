"""古建文旅规划助手 - API 速率限制

使用 slowapi（基于 limits 库）实现请求速率控制。
后端使用内存存储（进程内），适合单机部署。
如需分布式限流，可配置 Redis 后端。

限流策略：
    全局：          60 次/分钟
    AI 规划生成：    5 次/分钟  （LLM API 调用昂贵）
    合规校验：      10 次/分钟  （RAG 检索较重）
    方案修改：      10 次/分钟
    报告生成：       5 次/分钟
    普通 CRUD：     继承全局限制

配置：
    RATE_LIMIT_ENABLED=true|false  是否启用限流（默认 true）
    RATE_LIMIT_STORAGE=memory|redis 限流存储后端（默认 memory）
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse


# 创建限流器实例
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],  # 全局默认：60 次/分钟
    storage_uri="memory://",  # 内存存储，生产环境可改为 redis://...
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """自定义限流响应格式"""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "请求过于频繁，请稍后再试",
            "retry_after": exc.retry_after_seconds if hasattr(exc, "retry_after_seconds") else 60,
            "limit": str(exc.limit.limit) if hasattr(exc, "limit") else "unknown",
        },
        headers={"Retry-After": str(int(getattr(exc, "retry_after_seconds", 60)))},
    )


def get_rate_limit_key(request: Request) -> str:
    """获取限流键（客户端 IP）"""
    # 优先使用 X-Forwarded-For（如果经过代理）
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # 其次使用 X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    # 最后使用直连 IP
    if request.client:
        return request.client.host
    return "unknown"
