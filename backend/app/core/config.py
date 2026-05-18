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
    app_secret_key: str = ""  # 生产环境必须设置，否则启动时警告
    cors_origins: str = "http://localhost:3000"
    api_key: str = ""  # 生产环境建议设置，开发环境留空跳过认证

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
    neo4j_password: str = ""  # 生产环境必须设置
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
    minio_access_key: str = ""  # 生产环境必须设置
    minio_secret_key: str = ""  # 生产环境必须设置
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

    def check_production_secrets(self) -> list[str]:
        """检查生产环境缺失的关键配置，返回警告列表"""
        warnings = []
        if self.app_env == "production":
            if not self.app_secret_key:
                warnings.append("APP_SECRET_KEY 未设置")
            if not self.api_key:
                warnings.append("API_KEY 未设置（写操作无认证保护）")
            if self.neo4j_enabled and not self.neo4j_password:
                warnings.append("NEO4J_PASSWORD 未设置但 Neo4j 已启用")
            if not self.deepseek_api_key and not self.qwen_api_key and not self.openai_api_key:
                warnings.append("未配置任何 LLM API Key，AI 功能不可用")
        return warnings


@lru_cache
def get_settings() -> Settings:
    return Settings()
