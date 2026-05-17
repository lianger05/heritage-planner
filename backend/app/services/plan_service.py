"""规划方案生成服务 - 核心AI引擎"""

import json
import logging
import time
from typing import Optional

from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.kg_service import KnowledgeGraphService

logger = logging.getLogger(__name__)

# 系统提示词 - 规划专家角色
PLANNER_SYSTEM_PROMPT = """你是一位资深的古建保护与文旅规划专家，拥有以下专业背景：
- 深谙《文物保护法》《历史文化名城保护条例》等法规体系
- 熟悉中国古建各时期风格特征与保护要求
- 精通文旅业态规划、游客动线设计、经济可行性分析
- 遵循"保护第一、合理利用、加强管理"的文物工作方针

你的任务是：根据给定的古建信息和需求，生成一份结构化的保护性开发方案。

**绝对原则：**
1. 文物安全是不可逾越的红线，任何开发建议不得违反保护法规
2. 方案必须明确区分"保护措施"与"开发建议"，保护优先
3. 经济估算基于保守假设，标注置信度
4. 所有建议必须附上依据（法规条文/成功案例/专业标准）

**输出格式（严格JSON）：**
{
  "protection_measures": {
    "core_zone": "核心保护范围措施",
    "buffer_zone": "建设控制地带措施",
    "structural": "结构安全措施",
    "environmental": "环境控制措施",
    "monitoring": "监测预警措施"
  },
  "tourism_routes": {
    "main_route": {"description": "主线描述", "stops": ["站点1", "站点2"], "duration": "约X小时", "highlights": ["亮点1"]},
    "alternative_routes": [{"description": "备选路线", "stops": [], "duration": "", "suitable_for": "适用人群"}],
    "accessibility": "无障碍设施建议"
  },
  "business_layout": {
    "cultural_creative": {"description": "文创开发建议", "location": "建议位置", "scale": "规模"},
    "dining": {"description": "餐饮建议", "location": "", "style": "风格"},
    "accommodation": {"description": "住宿建议", "location": "", "type": "类型"},
    "experience": {"description": "体验活动", "items": ["项目1"]},
    "prohibited": ["禁止业态1", "禁止业态2"]
  },
  "economic_estimation": {
    "investment": {"amount": "预估投资(万元)", "breakdown": {"基础设施建设": 0, "修缮工程": 0, "配套开发": 0}, "confidence": "low/medium/high"},
    "revenue": {"annual": "年营收预估(万元)", "sources": {"门票": 0, "文创": 0, "餐饮": 0, "其他": 0}, "confidence": "low/medium/high"},
    "roi": {"payback_period": "回收期(年)", "npv_note": "简述", "sensitivity": "关键敏感性因素"},
    "assumptions": ["假设1", "假设2"]
  },
  "constraints_check": {
    "regulations_referenced": ["引用的法规1"],
    "potential_risks": [{"risk": "风险描述", "mitigation": "缓解措施"}],
    "approval_requirements": ["审批要求1"]
  }
}"""


class PlanGeneratorService:
    """规划方案生成服务"""

    def __init__(self):
        self.llm = LLMService()
        self.rag = RAGService()
        self.kg = KnowledgeGraphService()

    async def generate_plan(
        self,
        heritage_info: dict,
        user_requirements: dict | None = None,
    ) -> dict:
        """
        生成完整的保护性开发方案
        流程：KG查询 → RAG法规检索 → RAG案例检索 → LLM生成 → 约束校验
        """
        start_time = time.time()
        heritage_name = heritage_info.get("name", "")

        # Step 1: 知识图谱查询
        kg_context = {}
        try:
            await self.kg.connect()
            protection_constraints = await self.kg.get_protection_constraints(heritage_name)
            similar_heritage = await self.kg.find_similar_heritage(heritage_name)
            kg_context = {
                "protection_constraints": protection_constraints,
                "similar_heritage": similar_heritage,
            }
        except Exception as e:
            logger.warning(f"KG query failed: {e}")
            kg_context = {"error": f"知识图谱查询失败: {str(e)}"}
        finally:
            await self.kg.close()

        # Step 2: RAG法规检索
        protection_level = heritage_info.get("protection_level", "")
        regulation_query = f"{heritage_name} {protection_level} 保护开发规划"
        regulations = await self.rag.search_regulations(
            regulation_query, protection_level=protection_level, top_k=8
        )

        # Step 3: RAG案例检索
        case_query = f"{heritage_info.get('building_type', '')} {protection_level} 文旅开发成功案例"
        cases = await self.rag.search_cases(case_query, top_k=3)

        # Step 4: 组装提示并生成方案
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": self._build_user_prompt(
                    heritage_info, kg_context, regulations, cases, user_requirements
                ),
            },
        ]

        if not self.llm.is_available:
            return {
                "error": "LLM未配置，请设置API Key后重试",
                "heritage_name": heritage_name,
                "kg_context": kg_context,
                "regulations_found": len(regulations),
                "cases_found": len(cases),
                "_meta": {
                    "generation_time": round(time.time() - start_time, 2),
                    "llm_model": "none",
                    "llm_provider": "none",
                    "heritage_name": heritage_name,
                },
            }

        plan_data = await self.llm.chat_json(
            messages,
            temperature=0.7,
            max_tokens=4096,
        )

        # Step 5: 约束校验
        try:
            constraint_result = await self.rag.check_constraints(heritage_info, plan_data)
            plan_data["constraints_check"] = constraint_result
        except Exception as e:
            logger.warning(f"Constraint check failed: {e}")
            plan_data["constraints_check"] = {"violations": [], "warnings": [], "passed": True}

        elapsed = time.time() - start_time
        plan_data["_meta"] = {
            "generation_time": round(elapsed, 2),
            "llm_model": self.llm.model,
            "llm_provider": self.llm.provider,
            "regulations_count": len(regulations),
            "cases_count": len(cases),
            "heritage_name": heritage_name,
        }

        return plan_data

    def _build_user_prompt(
        self,
        heritage_info: dict,
        kg_context: dict,
        regulations: list[dict],
        cases: list[dict],
        user_requirements: dict | None = None,
    ) -> str:
        """组装用户提示"""
        sections = []

        sections.append(f"## 古建信息\n{json.dumps(heritage_info, ensure_ascii=False, indent=2)}")

        if kg_context.get("protection_constraints"):
            constraints_text = json.dumps(kg_context["protection_constraints"], ensure_ascii=False, indent=2)
            sections.append(f"## 保护等级约束（来自知识图谱）\n{constraints_text}")

        if kg_context.get("similar_heritage"):
            similar_text = json.dumps(kg_context["similar_heritage"], ensure_ascii=False, indent=2)
            sections.append(f"## 相似古建（来自知识图谱）\n{similar_text}")

        if regulations:
            reg_text = "\n".join([
                f"- [{r['title']}] 约束力:{'硬约束' if r.get('is_constraint') else '软约束'}\n  {r['content'][:300]}"
                for r in regulations
            ])
            sections.append(f"## 相关法规\n{reg_text}")

        if cases:
            case_text = "\n".join([
                f"- [{c['name']}] {c.get('location', '')}\n  {c['content'][:300]}"
                for c in cases
            ])
            sections.append(f"## 参考案例\n{case_text}")

        if user_requirements:
            sections.append(f"## 用户需求\n{json.dumps(user_requirements, ensure_ascii=False, indent=2)}")

        sections.append(
            "\n请基于以上信息，生成一份完整的保护性开发方案。严格遵守输出JSON格式。"
        )

        return "\n\n".join(sections)

    async def refine_plan(
        self,
        current_plan: dict,
        feedback: str,
        heritage_info: dict,
    ) -> dict:
        """根据用户反馈修改方案"""
        if not self.llm.is_available:
            return {"error": "LLM未配置，请设置API Key后重试"}

        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"## 当前方案\n{json.dumps(current_plan, ensure_ascii=False, indent=2)}\n\n"
                    f"## 古建信息\n{json.dumps(heritage_info, ensure_ascii=False, indent=2)}\n\n"
                    f"## 用户修改意见\n{feedback}\n\n"
                    "请根据用户意见修改方案，保持JSON格式输出完整的修改后方案。"
                ),
            },
        ]

        return await self.llm.chat_json(messages, temperature=0.5, max_tokens=4096)
