"""古建文旅经济智能规划助手 - 后端应用配置"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，从环境变量读取"""

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = True
    app_name: str = "古建文旅经济智能规划助手"
    app_version: str = "0.1.0"
    app_secret_key: str = "change-this-in-production"
    cors_origins: str = "http://localhost:3000"

    # Database - 本地开发用 SQLite
    database_url: str = "sqlite+aiosqlite:///./data/heritage_planner.db"
    database_url_sync: str = "sqlite:///./data/heritage_planner.db"

    # LLM - DeepSeek (primary)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    # LLM - Qwen (fallback)
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"

    # LLM - OpenAI compatible (universal fallback)
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"

    # Redis (可选，本地开发跳过)
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False

    # Neo4j (可选，本地开发跳过)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "heritage2024"
    neo4j_enabled: bool = False

    # ChromaDB (可选，本地用嵌入式)
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_persist_dir: str = "./data/chroma_db"
    chroma_mode: str = "persistent"  # "http" | "persistent"
    chroma_collection_regulation: str = "heritage_regulations"
    chroma_collection_case: str = "heritage_cases"

    # MinIO (可选)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "heritage-planner"

    # Amap
    amap_api_key: str = ""
    amap_security_key: str = ""

    # LLM Cache
    llm_cache_enabled: bool = False
    llm_cache_ttl: int = 3600

    # Planning constraints
    max_plan_iterations: int = 5
    plan_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    plan_max_tokens: int = 4096

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
