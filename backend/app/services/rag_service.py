"""RAG政策检索服务 - 本地嵌入式ChromaDB"""

import json
import logging
import os
from typing import Optional

from app.core.config import get_settings
from app.core.sanitize import safe_json_for_prompt
from app.services.llm_service import LLMService

settings = get_settings()
logger = logging.getLogger(__name__)


class RAGService:
    """基于ChromaDB的政策法规检索服务（本地持久化模式）"""

    def __init__(self):
        self._client = None
        self.llm = LLMService()

    def _get_client(self):
        """延迟初始化ChromaDB客户端"""
        if self._client is not None:
            return self._client

        try:
            import chromadb
            os.makedirs(settings.chroma_persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
            logger.info(f"ChromaDB initialized at {settings.chroma_persist_dir}")
        except ImportError:
            logger.warning("chromadb not installed, RAG features disabled")
            self._client = None
        except Exception as e:
            logger.warning(f"ChromaDB init failed: {e}, RAG features disabled")
            self._client = None

        return self._client

    def _get_regulation_collection(self):
        client = self._get_client()
        if client is None:
            return None
        return client.get_or_create_collection(
            name=settings.chroma_collection_regulation,
            metadata={"hnsw:space": "cosine"},
        )

    def _get_case_collection(self):
        client = self._get_client()
        if client is None:
            return None
        return client.get_or_create_collection(
            name=settings.chroma_collection_case,
            metadata={"hnsw:space": "cosine"},
        )

    async def search_regulations(
        self,
        query: str,
        protection_level: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """检索相关法规"""
        collection = self._get_regulation_collection()
        if collection is None:
            return []

        try:
            where_filter = None
            if protection_level:
                where_filter = {"protection_levels": {"$contains": protection_level}}

            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )

            regulations = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    regulations.append({
                        "content": doc,
                        "title": meta.get("title", "未知"),
                        "source": meta.get("source", ""),
                        "level": meta.get("level", ""),
                        "protection_levels": meta.get("protection_levels", []),
                        "is_constraint": meta.get("is_constraint", True),
                        "relevance_score": round(1 - distance, 4),
                    })

            return regulations
        except Exception as e:
            logger.warning(f"RAG regulation search failed: {e}")
            return []

    async def search_cases(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:
        """检索相似成功案例"""
        collection = self._get_case_collection()
        if collection is None:
            return []

        try:
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            )

            cases = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    cases.append({
                        "content": doc,
                        "name": meta.get("name", "未知"),
                        "location": meta.get("location", ""),
                        "type": meta.get("type", ""),
                        "relevance_score": round(1 - distance, 4),
                    })

            return cases
        except Exception as e:
            logger.warning(f"RAG case search failed: {e}")
            return []

    async def check_constraints(
        self,
        heritage_info: dict,
        plan_content: dict,
    ) -> dict:
        """校验方案是否违反法规约束"""
        if not self.llm.is_available:
            return {"violations": [], "warnings": ["LLM不可用，无法进行约束校验"], "passed": False}

        # 1. 检索相关法规
        protection_level = heritage_info.get("protection_level", "")
        query = f"{heritage_info.get('name', '')} {protection_level} 保护开发规划约束"
        regulations = await self.search_regulations(query, protection_level=protection_level, top_k=10)

        # 2. 构建LLM校验提示
        reg_text = "\n".join([
            f"[{r['title']}]({r.get('source', '')}) (约束力: {'硬约束' if r.get('is_constraint') else '软约束'}):\n{r['content'][:500]}"
            for r in regulations
        ])

        messages = [
            {
                "role": "system",
                "content": (
                    "你是古建保护法规专家。你的任务是检查一个保护性开发方案是否违反相关法规。\n"
                    "请仔细对比方案内容与法规要求，输出JSON格式的校验结果。\n"
                    "输出格式：\n"
                    '{"violations": [{"regulation": "违反的法规", "issue": "具体问题", "severity": "high/medium/low"}], '
                    '"warnings": ["潜在风险提示"], "passed": true/false}'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"## 古建信息\n{safe_json_for_prompt(heritage_info)}\n\n"
                    f"## 相关法规\n{reg_text or '暂无检索到相关法规'}\n\n"
                    f"## 规划方案\n{safe_json_for_prompt(plan_content)}\n\n"
                    "请校验该方案是否存在违规问题。"
                ),
            },
        ]

        try:
            result = await self.llm.chat_json(messages, temperature=0.1)
            # 确保返回值包含 passed 字段且默认安全（校验失败时应为 False）
            if "passed" not in result:
                result["passed"] = False
            return result
        except Exception as e:
            # 校验异常时默认不通过，避免误放行违规方案
            return {"violations": [{"regulation": "校验服务异常", "issue": str(e), "severity": "high"}], "warnings": [f"约束校验失败: {str(e)}"], "passed": False}

    def add_regulation(
        self,
        doc_id: str,
        content: str,
        metadata: dict,
    ) -> bool:
        """添加法规到向量库"""
        collection = self._get_regulation_collection()
        if collection is None:
            return False

        try:
            collection.upsert(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata],
            )
            return True
        except Exception as e:
            logger.warning(f"Add regulation failed: {e}")
            return False

    def add_case(
        self,
        case_id: str,
        content: str,
        metadata: dict,
    ) -> bool:
        """添加案例到向量库"""
        collection = self._get_case_collection()
        if collection is None:
            return False

        try:
            collection.upsert(
                ids=[case_id],
                documents=[content],
                metadatas=[metadata],
            )
            return True
        except Exception as e:
            logger.warning(f"Add case failed: {e}")
            return False
