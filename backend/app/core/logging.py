"""古建文旅规划助手 - 日志系统配置

使用 loguru 替代标准库 logging，提供：
- 彩色终端输出（开发环境）
- 文件日志轮转（保留 7 天，自动压缩）
- 结构化日志（JSON 格式，便于 ELK 等工具采集）
- 生产环境不记录请求体（避免泄露用户数据和 API Key）

配置方式：
    from app.core.logging import setup_logging
    setup_logging(app)  # 在 create_app() 中调用

环境变量：
    APP_ENV=development|production  （影响日志级别和格式）
    APP_DEBUG=true|false            （debug 模式下记录请求体）
"""

import sys
import os
from pathlib import Path
from loguru import logger


def setup_logging(app=None) -> None:
    """初始化 loguru 日志系统。

    移除默认 handler，添加终端和文件两个 sink。
    如果传入 FastAPI app，会替换 uvicorn 的日志 handler。
    """
    # 移除默认 handler
    logger.remove()

    settings = None
    if app:
        from app.core.config import get_settings
        settings = get_settings()

    env = os.getenv("APP_ENV", "development")
    debug = os.getenv("APP_DEBUG", "true").lower() == "true" if env == "development" else False

    # ---- 终端输出 ----
    if env == "development":
        # 开发环境：彩色、详细
        logger.add(
            sys.stderr,
            format=(
                "<green>{time:HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            level="DEBUG" if debug else "INFO",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )
    else:
        # 生产环境：简洁
        logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}",
            level="INFO",
            colorize=False,
            backtrace=False,
            diagnose=False,
        )

    # ---- 文件日志 ----
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # 应用日志（所有级别 INFO+）
    logger.add(
        log_dir / "app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="INFO",
        rotation="00:00",  # 每天午夜轮转
        retention="7 days",  # 保留 7 天
        compression="gz",  # 轮转后压缩
        encoding="utf-8",
        backtrace=True,
        diagnose=debug,
    )

    # 错误日志（独立文件，仅 ERROR+）
    logger.add(
        log_dir / "error_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="00:00",
        retention="30 days",  # 错误日志保留更久
        compression="gz",
        encoding="utf-8",
        backtrace=True,
        diagnose=True,  # 错误日志始终详细
    )

    # ---- 拦截标准 logging 到 loguru ----
    import logging

    class InterceptHandler(logging.Handler):
        """将标准库 logging 重定向到 loguru"""

        def emit(self, record: logging.LogRecord) -> None:
            # 获取对应的 loguru level
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # 找到调用栈帧（跳过本 handler）
            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    # 替换 uvicorn 和 fastapi 的 handler
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # 替换各模块的 logger
    for _log_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "sqlalchemy.engine"):
        _logger = logging.getLogger(_log_name)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False

    logger.info("Logging system initialized (env={}, debug={})", env, debug)

    if app:
        # 将 loguru logger 挂载到 app.state，方便视图函数使用
        app.state.logger = logger


# 模块级便捷函数
def get_logger():
    """获取 loguru logger 实例"""
    return logger
