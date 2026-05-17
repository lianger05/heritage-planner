"""
RAG文档入库脚本 - 将法规和案例导入ChromaDB向量库
"""

import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from chromadb import HttpClient
from chromadb.config import Settings as ChromaSettings


def seed_regulations():
    """导入法规到向量库"""
    client = HttpClient(host="localhost", port=8000)

    collection = client.get_or_create_collection(
        name="heritage_regulations",
        metadata={"hnsw:space": "cosine"},
    )

    regulations = [
        {
            "id": "reg_national_001",
            "content": "《中华人民共和国文物保护法》规定：文物保护单位的保护范围内不得进行其他建设工程或者爆破、钻探、挖掘等作业。因特殊情况需要的，必须保证文物保护单位的安全，并经核定公布该文物保护单位的人民政府批准。全国重点文物保护单位的保护范围内进行其他建设工程的，必须经省级人民政府批准，在批准前应当征得国务院文物行政部门同意。建设控制地带内进行建设工程，不得破坏文物保护单位的历史风貌。",
            "metadata": {
                "title": "中华人民共和国文物保护法",
                "source": "全国人民代表大会常务委员会",
                "level": "国家",
                "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"], ensure_ascii=False),
                "is_constraint": True,
            },
        },
        {
            "id": "reg_national_002",
            "content": "《历史文化名城名镇名村保护条例》：在历史文化名城保护范围内从事建设活动，应当符合保护规划的要求，不得损害历史文化遗产的真实性和完整性。核心保护范围内不得进行新建、扩建活动（必要的基础设施和公共服务设施除外）。拆除历史建筑以外的建筑物、构筑物或其他设施的，应当经城乡规划主管部门会同文物主管部门批准。",
            "metadata": {
                "title": "历史文化名城名镇名村保护条例",
                "source": "国务院",
                "level": "国家",
                "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位"], ensure_ascii=False),
                "is_constraint": True,
            },
        },
        {
            "id": "reg_national_003",
            "content": "《文物保护工程管理办法》：文物保护工程必须遵守不改变文物原状的原则，全面地保存、延续文物的真实历史信息和价值。按照文物级别实行分级管理。全国重点文物保护单位保护工程由省级文物行政部门组织实施。修缮工程应当最小干预，尽可能保留原有构件，使用传统工艺和材料。",
            "metadata": {
                "title": "文物保护工程管理办法",
                "source": "国家文物局",
                "level": "国家",
                "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位"], ensure_ascii=False),
                "is_constraint": True,
            },
        },
        {
            "id": "reg_henan_001",
            "content": "《河南省文物保护条例》：省级文物保护单位的保护范围由省人民政府划定并公布。保护范围内禁止：(一)刻划、涂污、损坏文物；(二)进行与文物保护无关的建设工程；(三)存放易燃、易爆、放射性、腐蚀性等危险物品。建设控制地带内新建、改建、扩建建筑物，其风格、高度、体量、色调应当与文物保护单位的环境风貌相协调。",
            "metadata": {
                "title": "河南省文物保护条例",
                "source": "河南省人民代表大会常务委员会",
                "level": "省",
                "protection_levels": json.dumps(["省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"], ensure_ascii=False),
                "is_constraint": True,
            },
        },
        {
            "id": "reg_policy_001",
            "content": "《关于进一步加强文物工作的指导意见》：坚持"保护为主、抢救第一、合理利用、加强管理"的文物工作方针。在确保文物安全的前提下，积极拓展文物利用途径，推动文博单位开发文化创意产品。鼓励社会力量参与文物保护利用，支持非国有博物馆发展。发挥文物资源在传承中华优秀传统文化中的作用。",
            "metadata": {
                "title": "关于进一步加强文物工作的指导意见",
                "source": "国务院",
                "level": "国家",
                "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"], ensure_ascii=False),
                "is_constraint": False,
            },
        },
    ]

    for reg in regulations:
        collection.upsert(
            ids=[reg["id"]],
            documents=[reg["content"]],
            metadatas=[reg["metadata"]],
        )

    print(f"Seeded {len(regulations)} regulations into ChromaDB")


def seed_cases():
    """导入成功案例到向量库"""
    client = HttpClient(host="localhost", port=8000)

    collection = client.get_or_create_collection(
        name="heritage_cases",
        metadata={"hnsw:space": "cosine"},
    )

    cases = [
        {
            "id": "case_001",
            "content": "杭州良渚古城遗址：2019年列入世界遗产名录。采用"遗址+公园"模式，核心遗址区严格保护，外围建设良渚文化村提供配套服务。游客动线设计为博物馆→遗址区→文创体验区，年接待游客超200万人次。投资约30亿元，回收期约12年。成功经验：严格区分核心保护区与开发区域，文创收入占总收入40%以上。",
            "metadata": {
                "name": "良渚古城遗址",
                "location": "浙江杭州",
                "type": "古遗址",
            },
        },
        {
            "id": "case_002",
            "content": "苏州园林群：拙政园、留园等9座园林列入世界遗产。采用"分散入园、限流保护"策略，核心保护区内不增设商业设施，游客服务集中在园外区域。推出"园林一票通"串联多座园林，日均限流8000人次。年营收约2.5亿元，其中门票收入占50%，文创占30%。成功经验：以园林为核心打造全城文旅生态，而非单一景点开发。",
            "metadata": {
                "name": "苏州园林群",
                "location": "江苏苏州",
                "type": "园林",
            },
        },
        {
            "id": "case_003",
            "content": "平遥古城：1997年列入世界遗产。采用"城内保护、城外开发"模式，古城内严格控制商业业态，核心保护区内禁止新建建筑。游客动线为城墙→县衙→日升昌→明清街，夜游经济为特色。年接待游客超300万人次，旅游总收入超50亿元。成功经验：保护与开发空间分离，古城整体申遗提升品牌价值。",
            "metadata": {
                "name": "平遥古城",
                "location": "山西平遥",
                "type": "古城",
            },
        },
        {
            "id": "case_004",
            "content": "泉州开元寺：全国重点文物保护单位，采用"寺内严格保护+周边文旅配套"模式。寺内禁止商业活动，东西塔实行预约限流参观。周边西街改造为非遗体验街区，展示南音、提线木偶等。年游客量约150万人次，周边文创年收入约3000万元。成功经验：将寺庙保护与古城整体文旅结合，以非遗体验丰富游览内容。",
            "metadata": {
                "name": "泉州开元寺",
                "location": "福建泉州",
                "type": "寺庙",
            },
        },
    ]

    for case in cases:
        collection.upsert(
            ids=[case["id"]],
            documents=[case["content"]],
            metadatas=[case["metadata"]],
        )

    print(f"Seeded {len(cases)} cases into ChromaDB")


if __name__ == "__main__":
    seed_regulations()
    seed_cases()
