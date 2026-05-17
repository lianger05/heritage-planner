"""AI对话端点"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
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
async def send_message(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """多轮对话：用户与AI讨论规划方案"""
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
        # 新建会话
        messages = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
            {
                "role": "system",
                "content": f"当前方案：\n{str(plan.protection_measures or {})}\n{str(plan.tourism_routes or {})}\n{str(plan.business_layout or {})}",
            },
            {"role": "user", "content": data.message},
        ]
    else:
        # 继续会话
        messages = session.messages or []
        messages = [
            {"role": "system", "content": CHAT_SYSTEM_PROMPT},
        ] + messages + [{"role": "user", "content": data.message}]

    # 调用LLM
    llm = LLMService()
    reply = await llm.chat(messages, temperature=0.7, max_tokens=2048)

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
        references=None,
    )


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
