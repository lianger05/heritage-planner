"""输入净化工具 — 防止 LLM Prompt 注入

提供用户输入的净化和截断功能：
1. 长度截断：防止超长输入导致 token 爆炸
2. 关键词过滤：移除常见的 prompt 注入模式
3. JSON 序列化安全：确保用户数据作为数据注入而非指令
"""

import re
from typing import Any

# Prompt 注入常见关键词模式（大小写不敏感）
_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+instructions",
    r"forget\s+(everything|all|previous)",
    r"you\s+are\s+now\s+",
    r"new\s+instructions?\s*:",
    r"system\s*:\s*",
    r"disregard\s+",
    r"override\s+(previous|all|default)\s+",
    r"pretend\s+(you\s+are|to\s+be)",
    r"jailbreak",
    r"DAN\s+mode",
]

_COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]

# 各场景的最大输入长度
MAX_LENGTHS = {
    "chat_message": 4000,
    "plan_feedback": 2000,
    "heritage_description": 5000,
    "search_query": 500,
    "default": 4000,
}


def sanitize_input(
    text: str,
    max_length: int | None = None,
    context: str = "default",
) -> str:
    """净化用户输入

    Args:
        text: 原始用户输入
        max_length: 最大允许长度（字符数），None 则按 context 取默认值
        context: 输入场景，用于确定默认截断长度

    Returns:
        净化后的字符串
    """
    if not text:
        return text

    # 1. 截断
    limit = max_length or MAX_LENGTHS.get(context, MAX_LENGTHS["default"])
    if len(text) > limit:
        text = text[:limit] + f"...[截断：原始输入超过 {limit} 字符]"

    # 2. 移除注入模式
    for pattern in _COMPILED_PATTERNS:
        text = pattern.sub("[已过滤]", text)

    return text


def safe_json_for_prompt(data: Any, max_str_length: int = 2000) -> str:
    """将数据安全序列化为 JSON，用于嵌入 LLM prompt

    对 JSON 字符串值进行截断，防止用户通过数据字段注入超长内容。
    将序列化结果包裹在 markdown code block 中，进一步降低 LLM 误读为指令的风险。

    Args:
        data: 要序列化的数据
        max_str_length: 单个字符串字段的最大长度

    Returns:
        安全的 JSON 字符串
    """
    import json

    def _truncate_strings(obj: Any) -> Any:
        if isinstance(obj, str):
            if len(obj) > max_str_length:
                return obj[:max_str_length] + "...[截断]"
            return obj
        if isinstance(obj, dict):
            return {k: _truncate_strings(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_truncate_strings(item) for item in obj]
        return obj

    truncated = _truncate_strings(data)
    json_str = json.dumps(truncated, ensure_ascii=False, indent=2)
    return f"```\n{json_str}\n```"
