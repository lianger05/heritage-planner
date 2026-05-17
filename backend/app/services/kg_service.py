"""知识图谱服务 - 本地内存模式（无Neo4j时降级）"""

import logging
from typing import Optional

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# 知识图谱种子数据（本地内存存储）
_SEED_DYNASTIES = [
    {"name": "唐", "period": "618-907", "description": "中国封建社会的鼎盛时期"},
    {"name": "宋", "period": "960-1279", "description": "经济文化高度发达，建筑技术成熟"},
    {"name": "辽", "period": "907-1125", "description": "契丹族政权，建筑融合汉辽风格"},
    {"name": "金", "period": "1115-1234", "description": "女真族政权，建筑承袭宋辽传统"},
    {"name": "元", "period": "1271-1368", "description": "蒙古族政权，建筑多元融合"},
    {"name": "明", "period": "1368-1644", "description": "建筑规制严格，官式建筑成熟"},
    {"name": "清", "period": "1644-1912", "description": "建筑装饰华丽，工艺精湛"},
    {"name": "民国", "period": "1912-1949", "description": "中西建筑风格交汇期"},
]

_SEED_STYLES = [
    {"name": "官式建筑", "description": "按照官方颁布的建筑规范建造的建筑，多见于宫殿、寺庙"},
    {"name": "地方民居", "description": "具有地方特色的民间建筑，如四合院、土楼等"},
    {"name": "园林建筑", "description": "以景观营造为核心的建筑形式"},
    {"name": "宗教建筑", "description": "寺庙、道观、清真寺等宗教场所"},
    {"name": "军事建筑", "description": "城墙、堡垒、烽火台等军事设施"},
]

_SEED_PROTECTION_LEVELS = {
    "全国重点文物保护单位": [
        "不得改变文物原状",
        "不得进行与保护无关的建设工程",
        "保护范围内不得进行其他建设工程",
        "建设控制地带内不得建设危及文物安全的设施",
        "修缮必须经省级文物行政部门批准",
        "迁移或拆除须经国务院批准",
    ],
    "省级文物保护单位": [
        "不得改变文物原状",
        "保护范围内不得进行其他建设工程",
        "修缮须经文物行政部门批准",
    ],
    "市级文物保护单位": [
        "不得擅自改变文物原状",
        "保护范围内建设工程需审批",
    ],
    "区县级文物保护单位": [
        "不得擅自拆除或改建",
        "建设活动需报文物部门备案",
    ],
}

_SEED_HERITAGE = [
    {
        "name": "铁塔",
        "dynasty": "宋",
        "protection_level": "全国重点文物保护单位",
        "building_type": "楼阁",
        "style": "宗教建筑",
        "province": "河南",
        "city": "开封",
        "description": "北宋皇佑元年(1049年)建，琉璃砖塔，高55.88米，八角十三层",
    },
    {
        "name": "龙亭",
        "dynasty": "清",
        "protection_level": "省级文物保护单位",
        "building_type": "宫殿",
        "style": "官式建筑",
        "province": "河南",
        "city": "开封",
        "description": "清代万寿宫建筑群，位于北宋故宫遗址之上",
    },
    {
        "name": "大相国寺",
        "dynasty": "唐",
        "protection_level": "全国重点文物保护单位",
        "building_type": "寺庙",
        "style": "宗教建筑",
        "province": "河南",
        "city": "开封",
        "description": "始建于北齐天保六年(555年)，唐宋时期著名寺院",
    },
    {
        "name": "繁塔",
        "dynasty": "宋",
        "protection_level": "全国重点文物保护单位",
        "building_type": "楼阁",
        "style": "宗教建筑",
        "province": "河南",
        "city": "开封",
        "description": "北宋太平兴国二年(977年)建，开封现存最古老的地面建筑",
    },
    {
        "name": "山陕甘会馆",
        "dynasty": "清",
        "protection_level": "全国重点文物保护单位",
        "building_type": "民居",
        "style": "地方民居",
        "province": "河南",
        "city": "开封",
        "description": "清代山西、陕西、甘肃三省旅汴商人集资兴建的会馆建筑",
    },
]


class KnowledgeGraphService:
    """知识图谱服务 - 本地内存降级模式"""

    def __init__(self):
        self._neo4j_driver = None
        self._use_memory = not settings.neo4j_enabled

        if not self._use_memory:
            try:
                from neo4j import AsyncGraphDatabase
                self._neo4j_driver = AsyncGraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password),
                )
                logger.info("Neo4j driver initialized")
            except Exception as e:
                logger.warning(f"Neo4j connection failed: {e}, falling back to memory mode")
                self._use_memory = True

    async def connect(self):
        """兼容原接口"""
        pass

    async def close(self):
        """关闭连接"""
        if self._neo4j_driver:
            await self._neo4j_driver.close()

    async def get_protection_constraints(self, heritage_name: str) -> list[dict]:
        """查询古建的保护等级约束"""
        if self._use_memory:
            # 从内存种子数据查找
            for h in _SEED_HERITAGE:
                if h["name"] == heritage_name:
                    level = h.get("protection_level", "")
                    constraints = _SEED_PROTECTION_LEVELS.get(level, [])
                    return [{"level": level, "constraints": constraints}]
            return []
        else:
            query = """
            MATCH (h:Heritage {name: $name})-[:HAS_PROTECTION]->(p:ProtectionLevel)
            RETURN p.name AS level, p.constraints AS constraints
            """
            async with self._neo4j_driver.session() as session:
                result = await session.run(query, {"name": heritage_name})
                return await result.data()

    async def find_similar_heritage(self, heritage_name: str, limit: int = 5) -> list[dict]:
        """通过图谱关系查找相似古建"""
        if self._use_memory:
            # 简单相似度：同朝代 + 同风格 + 同保护等级
            target = None
            for h in _SEED_HERITAGE:
                if h["name"] == heritage_name:
                    target = h
                    break

            if not target:
                return []

            similar = []
            for h in _SEED_HERITAGE:
                if h["name"] == heritage_name:
                    continue
                commonality = 0
                if h.get("dynasty") == target.get("dynasty"):
                    commonality += 1
                if h.get("style") == target.get("style"):
                    commonality += 1
                if h.get("protection_level") == target.get("protection_level"):
                    commonality += 1
                if h.get("building_type") == target.get("building_type"):
                    commonality += 1
                if commonality > 0:
                    similar.append({
                        "name": h["name"],
                        "city": h["city"],
                        "protection_level": h["protection_level"],
                        "commonality": commonality,
                    })

            similar.sort(key=lambda x: x["commonality"], reverse=True)
            return similar[:limit]
        else:
            query = """
            MATCH (h:Heritage {name: $name})-[:HAS_STYLE|BUILT_IN|HAS_TYPE]->(prop)<-[:HAS_STYLE|BUILT_IN|HAS_TYPE]-(other:Heritage)
            WHERE other.name <> $name
            WITH other, count(prop) AS commonality
            ORDER BY commonality DESC
            LIMIT $limit
            RETURN other.name AS name, other.city AS city, other.protection_level AS level, commonality
            """
            async with self._neo4j_driver.session() as session:
                result = await session.run(query, {"name": heritage_name, "limit": limit})
                return await result.data()

    async def get_heritage_full_context(self, heritage_name: str) -> dict:
        """获取古建的完整图谱上下文"""
        if self._use_memory:
            for h in _SEED_HERITAGE:
                if h["name"] == heritage_name:
                    return {
                        "heritage": h,
                        "dynasty": next((d for d in _SEED_DYNASTIES if d["name"] == h.get("dynasty")), None),
                        "style": next((s for s in _SEED_STYLES if s["name"] == h.get("style")), None),
                        "protection_level": {
                            "name": h.get("protection_level"),
                            "constraints": _SEED_PROTECTION_LEVELS.get(h.get("protection_level", ""), []),
                        },
                    }
            return {}
        else:
            query = """
            MATCH (h:Heritage {name: $name})
            OPTIONAL MATCH (h)-[:BUILT_IN]->(d:Dynasty)
            OPTIONAL MATCH (h)-[:HAS_STYLE]->(s:Style)
            OPTIONAL MATCH (h)-[:HAS_PROTECTION]->(p:ProtectionLevel)
            RETURN h, d, s, p
            """
            async with self._neo4j_driver.session() as session:
                result = await session.run(query, {"name": heritage_name})
                return await result.data()

    async def init_seed_data(self) -> None:
        """初始化知识图谱种子数据（Neo4j模式下写入，内存模式不需要）"""
        if self._use_memory:
            logger.info("KG seed data loaded in memory mode (5 heritage sites)")
            return

        # Neo4j 模式：写入种子数据
        try:
            async with self._neo4j_driver.session() as session:
                # 朝代
                for d in _SEED_DYNASTIES:
                    await session.run(
                        "MERGE (d:Dynasty {name: $name}) SET d.period = $period, d.description = $description",
                        d,
                    )

                # 风格
                for s in _SEED_STYLES:
                    await session.run(
                        "MERGE (s:Style {name: $name}) SET s.description = $description",
                        s,
                    )

                # 保护等级
                for name, constraints in _SEED_PROTECTION_LEVELS.items():
                    await session.run(
                        "MERGE (p:ProtectionLevel {name: $name}) SET p.constraints = $constraints",
                        {"name": name, "constraints": constraints},
                    )

                # 古建
                for h in _SEED_HERITAGE:
                    await session.run(
                        """MERGE (h:Heritage {name: $name})
                        SET h.dynasty = $dynasty, h.protection_level = $protection_level,
                            h.building_type = $building_type, h.style = $style,
                            h.province = $province, h.city = $city, h.description = $description""",
                        h,
                    )
                    if h.get("dynasty"):
                        await session.run(
                            """MATCH (h:Heritage {name: $hn}) MATCH (d:Dynasty {name: $dn})
                            MERGE (h)-[:BUILT_IN]->(d)""",
                            {"hn": h["name"], "dn": h["dynasty"]},
                        )
                    if h.get("style"):
                        await session.run(
                            """MATCH (h:Heritage {name: $hn}) MATCH (s:Style {name: $sn})
                            MERGE (h)-[:HAS_STYLE]->(s)""",
                            {"hn": h["name"], "sn": h["style"]},
                        )
                    if h.get("protection_level"):
                        await session.run(
                            """MATCH (h:Heritage {name: $hn}) MATCH (p:ProtectionLevel {name: $pn})
                            MERGE (h)-[:HAS_PROTECTION]->(p)""",
                            {"hn": h["name"], "pn": h["protection_level"]},
                        )

            logger.info("KG seed data initialized in Neo4j")
        except Exception as e:
            logger.warning(f"KG seed data init failed: {e}")
