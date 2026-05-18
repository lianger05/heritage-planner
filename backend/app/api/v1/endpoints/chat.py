"""AI对话端点"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.sanitize import sanitize_input, safe_json_for_prompt
from app.models.heritage import Plan, ChatSession
from app.schemas.heritage import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.services.plan_service import PlanGeneratorService

router = APIRouter()

# 多轮对话的系统提示
CHAT_SYSTEM_PROMPT = """你是古建保护与文旅规划专家助手，正在帮助用户完善一份保护性开发方案。

你的工作方式：
1. 基于当前方案内容和古建信息回答用户问题
2. 对方案提出具体的修改建议
3. 当用户要求修改时，输出更新后的方案片段
4. 主动提醒用户注意法规约束和保护红线
5. 引用具体法规或案例支撑你的建议

回答要求：
- 专业、具体、可操作
- 引用依据（法规条文/案例/标准）
- 修改建议以JSON片段形式输出，方便前端更新"""


@router.post("/message", response_model=ChatResponse, summary="发送对话消息")
@limiter.limit("10/minute")
async def send_message(
    request: Request,
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """多轮对话：用户与AI讨论规划方案"""
    # 净化用户输入（防 Prompt 注入 + 长度截断）
    safe_message = sanitize_input(data.message, context="chat_message")

    # 获取方案
    result = await db.execute(select(Plan).where(Plan.id == data.plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="方案未找到")

    # 获取或创建会话
    session_id = data.session_id or str(uuid.uuid4())
    session_result = await db.execute(
        select(ChatSession).where(ChatSession.session_id == session_id)
    )
    session = session_result.scalar_one_or_none()

    if not session:
        # 新建会话 — 使用 safe_json_for_prompt 防止方案数据被误读为指令
        messages = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
            {
                "role": "system",
                "content": f"当前方案数据：\n{safe_json_for_prompt({'protection_measures': plan.protection_measures, 'tourism_routes': plan.tourism_routes, 'business_layout': plan.business_layout})}",
            },
            {"role": "user", "content": safe_message},
        ]
    else:
        # 继续会话
        messages = session.messages or []
        messages = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        ] + messages + [{"role": "user", "content": safe_message}]

    # 调用LLM
    llm = LLMService()
    reply = await llm.chat(messages, temperature=0.7, max_tokens=2048)

    # 尝试从回复中提取方案更新片段
    updated_plan = _extract_plan_fragment(reply)

    # 更新会话
    new_messages = messages[1:] + [{"role": "assistant", "content": reply}]  # 去掉system prompt
    # 只保留最近20条消息
    new_messages = new_messages[-20:]

    if session:
        session.messages = new_messages
    else:
        session = ChatSession(
            plan_id=data.plan_id,
            session_id=session_id,
            messages=new_messages,
        )
        db.add(session)

    await db.flush()

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        updated_plan=updated_plan,
        references=None,
    )


def _extract_plan_fragment(reply: str) -> dict | None:
    """尝试从 AI 回复中提取 JSON 格式的方案更新片段。

    如果 AI 回复中包含 ```json ... ``` 代码块，则尝试解析为 dict。
    解析失败时返回 None（表示回复中无方案更新）。
    """
    import json
    import re

    # 匹配 ```json ... ``` 代码块
    json_blocks = re.findall(r"```json\s*\n?(.*?)```", reply, re.DOTALL)
    for block in json_blocks:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    # 匹配纯 JSON 对象（以 { 开头，} 结尾的多行文本）
    brace_match = re.search(r"\{[^{}]*\}", reply, re.DOTALL)
    if brace_match:
        try:
            parsed = json.loads(brace_match.group())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    return None


@router.get("/history/{session_id}", summary="获取对话历史")
async def get_chat_history(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(ChatSession.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="会话未找到")
    return {"session_id": session_id, "messages": session.messages}
