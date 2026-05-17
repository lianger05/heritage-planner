"""LLM服务封装 - 多供应商切换与本地内存缓存"""

import json
import time
from typing import AsyncGenerator, Optional

from openai import AsyncOpenAI

from app.core.config import get_settings

settings = get_settings()

# LLM供应商配置
LLM_PROVIDERS = {
    "deepseek": {
        "api_key": settings.deepseek_api_key,
        "base_url": settings.deepseek_base_url,
        "model": settings.deepseek_model,
    },
    "qwen": {
        "api_key": settings.qwen_api_key,
        "base_url": settings.qwen_base_url,
        "model": settings.qwen_model,
    },
    "openai": {
        "api_key": settings.openai_api_key,
        "base_url": settings.openai_base_url,
        "model": settings.openai_model,
    },
}

# 本地内存缓存（替代Redis）
_local_cache: dict[str, tuple[str, float]] = {}


class LLMService:
    """统一的LLM调用服务，支持多供应商切换"""

    def __init__(self, provider: str = "deepseek", redis=None):
        self.provider = provider
        config = LLM_PROVIDERS.get(provider)
        if not config or not config["api_key"]:
            # fallback到下一个可用供应商
            for p, c in LLM_PROVIDERS.items():
                if c["api_key"]:
                    provider = p
                    config = c
                    break

        if not config or not config["api_key"]:
            # 没有任何API Key可用
            self.client = None
            self.model = "none"
            self.provider = "none"
        else:
            self.client = AsyncOpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"],
            )
            self.model = config["model"]
            self.provider = provider

    @property
    def is_available(self) -> bool:
        """LLM是否可用"""
        return self.client is not None

    def _cache_get(self, key: str) -> Optional[str]:
        """从本地缓存获取"""
        if not settings.llm_cache_enabled:
            return None
        if key in _local_cache:
            content, ts = _local_cache[key]
            if time.time() - ts < settings.llm_cache_ttl:
                return content
            del _local_cache[key]
        return None

    def _cache_set(self, key: str, value: str) -> None:
        """写入本地缓存"""
        if settings.llm_cache_enabled:
            _local_cache[key] = (value, time.time())

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: dict | None = None,
        use_cache: bool = True,
    ) -> str:
        """发送聊天请求"""
        if not self.is_available:
            return json.dumps({
                "error": "LLM未配置API Key，请在 .env 中设置 DEEPSEEK_API_KEY / QWEN_API_KEY / OPENAI_API_KEY",
                "hint": "至少需要配置一个LLM供应商的API Key",
            })

        # 缓存检查
        cache_key = None
        if use_cache:
            cache_key = f"llm:{self.provider}:{self.model}:{hash(json.dumps(messages, ensure_ascii=False))}"
            cached = self._cache_get(cache_key)
            if cached:
                return cached

        # 调用LLM
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            kwargs["response_format"] = response_format

        start_time = time.time()
        response = await self.client.chat.completions.create(**kwargs)
        elapsed = time.time() - start_time

        content = response.choices[0].message.content

        # 写入缓存
        if cache_key:
            self._cache_set(cache_key, content)

        return content

    async def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        if not self.is_available:
            yield "[LLM未配置]"
            return

        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def chat_json(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """请求JSON格式输出"""
        content = await self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "LLM输出无法解析为JSON", "raw_content": content[:500]}
