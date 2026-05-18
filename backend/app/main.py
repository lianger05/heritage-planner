"""古建文旅经济智能规划助手 - FastAPI 应用入口"""

import uuid
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings


class RequestBodyLoggingMiddleware(BaseHTTPMiddleware):
    """诊断中间件：记录 POST/PUT/PATCH 请求体内容（仅 DEBUG 模式）"""

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        if settings.app_debug and request.method in ("POST", "PUT", "PATCH"):
            content_type = request.headers.get("content-type", "")
            body_bytes = await request.body()
            body_preview = body_bytes[:500].decode("utf-8", errors="replace") if body_bytes else "(empty)"
            logger.info(
                "REQ %s %s | Content-Type=%s | body_len=%d | body=%s",
                request.method, request.url.path, content_type, len(body_bytes), body_preview,
            )
        response = await call_next(request)
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期：启动与关闭"""
    settings = get_settings()

    # Startup: 初始化数据库
    logger.info("{} v{} starting (env={})", settings.app_name, settings.app_version, settings.app_env)

    from app.core.database import init_db, async_session_factory
    await init_db()
    logger.info("Database initialized (SQLite)")

    # 加载种子数据
    from app.core.seed import seed_database
    async with async_session_factory() as session:
        await seed_database(session)
    logger.info("Seed data loaded")

    # LLM 状态
    from app.services.llm_service import LLMService
    llm = LLMService()
    if llm.is_available:
        logger.info("LLM Primary: {}/{}", llm.provider, llm.model)
    else:
        logger.warning("LLM: 未配置API Key，方案生成功能不可用")

    # 生产环境安全检查
    security_warnings = settings.check_production_secrets()
    for w in security_warnings:
        logger.warning("PROD SECURITY: {}", w)

    yield

    # Shutdown
    logger.info("{} shutting down...", settings.app_name)


def create_app() -> FastAPI:
    settings = get_settings()

    # 初始化日志系统（最先执行）
    from app.core.logging import setup_logging

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="古建文旅经济智能规划助手 API - 自动生成保护性开发方案",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )
    setup_logging(app)

    # 请求体诊断中间件（调试用，部署时可关闭 APP_DEBUG=false）
    app.add_middleware(RequestBodyLoggingMiddleware)

    # CORS — 限定具体域名，开发环境兼容 localhost
    cors_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
    if "*" in cors_origins:
        cors_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=False if "*" in cors_origins else True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # API Key 认证中间件
    from app.core.auth import api_key_middleware
    app.middleware("http")(api_key_middleware)

    # --- 异常处理器 ---

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """自定义验证异常，返回更详细的错误信息"""
        logger.warning(
            "Validation error on {} {}: {}",
            request.method, request.url.path, exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Request validation failed",
                "errors": exc.errors(),
                "hint": "检查请求体字段名和类型是否与API schema匹配。查看 /api/docs 获取完整schema。",
            },
        )

    # 速率限制异常处理器
    from app.core.rate_limit import limiter, rate_limit_exceeded_handler

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局未捕获异常处理器"""
        error_id = str(uuid.uuid4())[:8]
        logger.error(
            "Unhandled exception [{}] on {} {}: {}",
            error_id, request.method, request.url.path, str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_id": error_id,
                "hint": "若持续出现，请联系管理员并提供 error_id",
            },
        )

    # Routes
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
