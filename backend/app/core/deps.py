"""服务层依赖注入 — 避免每次请求重新实例化服务

使用 FastAPI 的 Depends 机制注入服务实例。
对于无状态服务（如 LLMService、RAGService），使用 lru_cache 单例；
对于有状态服务，使用请求级依赖。
"""

from functools import lru_cache

from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.plan_service import PlanGeneratorService


@lru_cache
def get_llm_service() -> LLMService:
    """获取 LLM 服务单例"""
    return LLMService()


@lru_cache
def get_rag_service() -> RAGService:
    """获取 RAG 服务单例"""
    return RAGService()


def get_plan_service() -> PlanGeneratorService:
    """获取规划方案生成服务（每次新建，因为组合了多个子服务）"""
    return PlanGeneratorService()
