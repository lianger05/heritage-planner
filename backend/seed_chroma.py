"""
RAG文档入库脚本 - 将法规和案例导入ChromaDB向量库（本地持久化模式）
"""

import json
import os

# 确保data目录存在
CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma_db")
os.makedirs(CHROMA_DIR, exist_ok=True)

import chromadb


def seed_regulations():
    """导入法规到向量库"""
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.get_or_create_collection(
        name="heritage_regulations",
        metadata={"hnsw:space": "cosine"},
    )

    regulations = [
        {
            "id": "reg_national_001",
            "content": (
                "\u300a\u4e2d\u534e\u4eba\u6c11\u5171\u548c\u56fd\u6587\u7269\u4fdd\u62a4\u6cd5\u300b"
                "\u89c4\u5b9a\uff1a\u6587\u7269\u4fdd\u62a4\u5355\u4f4d\u7684\u4fdd\u62a4\u8303\u56f4"
                "\u5185\u4e0d\u5f97\u8fdb\u884c\u5176\u4ed6\u5efa\u8bbe\u5de5\u7a0b\u6216\u8005\u7206"
                "\u7834\u3001\u94bb\u63a2\u3001\u6316\u6398\u7b49\u4f5c\u4e1a\u3002\u56e0\u7279\u6b8a"
                "\u60c5\u51b5\u9700\u8981\u7684\uff0c\u5fc5\u987b\u4fdd\u8bc1\u6587\u7269\u4fdd\u62a4"
                "\u5355\u4f4d\u7684\u5b89\u5168\uff0c\u5e76\u7ecf\u6838\u5b9a\u516c\u5e03\u8be5\u6587"
                "\u7269\u4fdd\u62a4\u5355\u4f4d\u7684\u4eba\u6c11\u653f\u5e9c\u6279\u51c6\u3002\u5168"
                "\u56fd\u91cd\u70b9\u6587\u7269\u4fdd\u62a4\u5355\u4f4d\u7684\u4fdd\u62a4\u8303\u56f4"
                "\u5185\u8fdb\u884c\u5176\u4ed6\u5efa\u8bbe\u5de5\u7a0b\u7684\uff0c\u5fc5\u987b\u7ecf"
                "\u7701\u7ea7\u4eba\u6c11\u653f\u5e9c\u6279\u51c6\uff0c\u5728\u6279\u51c6\u524d\u5e94"
                "\u5f53\u5f81\u5f97\u56fd\u52a1\u9662\u6587\u7269\u884c\u653f\u90e8\u95e8\u540c\u610f"
                "\u3002\u5efa\u8bbe\u63a7\u5236\u5730\u5e26\u5185\u8fdb\u884c\u5efa\u8bbe\u5de5\u7a0b"
                "\uff0c\u4e0d\u5f97\u7834\u574f\u6587\u7269\u4fdd\u62a4\u5355\u4f4d\u7684\u5386\u53f2"
                "\u98ce\u8c8c\u3002"
            ),
            "metadata": {
                "title": "\u4e2d\u534e\u4eba\u6c11\u5171\u548c\u56fd\u6587\u7269\u4fdd\u62a4\u6cd5",
                "source": "\u5168\u56fd\u4eba\u6c11\u4ee3\u8868\u5927\u4f1a\u5e38\u52a1\u59d4\u5458\u4f1a",
                "level": "\u56fd\u5bb6",
                "protection_levels": json.dumps(
                    ["\u5168\u56fd\u91cd\u70b9\u6587\u7269\u4fdd\u62a4\u5355\u4f4d",
                     "\u7701\u7ea7\u6587\u7269\u4fdd\u62a4\u5355\u4f4d",
                     "\u5e02\u7ea7\u6587\u7269\u4fdd\u62a4\u5355\u4f4d",
                     "\u533a\u53bf\u7ea7\u6587\u7269\u4fdd\u62a4\u5355\u4f4d"],
                    ensure_ascii=False
                ),
                "is_constraint": True,
            },
        },
    ]

    # ... 用更简单的方式：直接从data目录读取
    # 为了避免编码问题，直接用字典构建

    regs_data = [
        ("reg_national_001",
         "《中华人民共和国文物保护法》规定：文物保护单位的保护范围内不得进行其他建设工程或者爆破、钻探、挖掘等作业。因特殊情况需要的，必须保证文物保护单位的安全，并经核定公布该文物保护单位的人民政府批准。全国重点文物保护单位的保护范围内进行其他建设工程的，必须经省级人民政府批准，在批准前应当征得国务院文物行政部门同意。建设控制地带内进行建设工程，不得破坏文物保护单位的历史风貌。",
         {"title": "中华人民共和国文物保护法", "source": "全国人民代表大会常务委员会", "level": "国家",
          "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"], ensure_ascii=False),
          "is_constraint": True}),

        ("reg_national_002",
         "《历史文化名城名镇名村保护条例》：在历史文化名城保护范围内从事建设活动，应当符合保护规划的要求，不得损害历史文化遗产的真实性和完整性。核心保护范围内不得进行新建、扩建活动（必要的基础设施和公共服务设施除外）。拆除历史建筑以外的建筑物、构筑物或其他设施的，应当经城乡规划主管部门会同文物主管部门批准。",
         {"title": "历史文化名城名镇名村保护条例", "source": "国务院", "level": "国家",
          "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位"], ensure_ascii=False),
          "is_constraint": True}),

        ("reg_national_003",
         "《文物保护工程管理办法》：文物保护工程必须遵守不改变文物原状的原则，全面地保存、延续文物的真实历史信息和价值。按照文物级别实行分级管理。全国重点文物保护单位保护工程由省级文物行政部门组织实施。修缮工程应当最小干预，尽可能保留原有构件，使用传统工艺和材料。",
         {"title": "文物保护工程管理办法", "source": "国家文物局", "level": "国家",
          "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位"], ensure_ascii=False),
          "is_constraint": True}),

        ("reg_henan_001",
         "《河南省文物保护条例》：省级文物保护单位的保护范围由省人民政府划定并公布。保护范围内禁止：(一)刻划、涂污、损坏文物；(二)进行与文物保护无关的建设工程；(三)存放易燃、易爆、放射性、腐蚀性等危险物品。建设控制地带内新建、改建、扩建建筑物，其风格、高度、体量、色调应当与文物保护单位的环境风貌相协调。",
         {"title": "河南省文物保护条例", "source": "河南省人民代表大会常务委员会", "level": "省",
          "protection_levels": json.dumps(["省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"], ensure_ascii=False),
          "is_constraint": True}),

        ("reg_policy_001",
         "《关于进一步加强文物工作的指导意见》：坚持保护为主、抢救第一、合理利用、加强管理的文物工作方针。在确保文物安全的前提下，积极拓展文物利用途径，推动文博单位开发文化创意产品。鼓励社会力量参与文物保护利用，支持非国有博物馆发展。发挥文物资源在传承中华优秀传统文化中的作用。",
         {"title": "关于进一步加强文物工作的指导意见", "source": "国务院", "level": "国家",
          "protection_levels": json.dumps(["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"], ensure_ascii=False),
          "is_constraint": False}),
    ]

    for reg_id, content, metadata in regs_data:
        collection.upsert(
            ids=[reg_id],
            documents=[content],
            metadatas=[metadata],
        )

    print(f"Seeded {len(regs_data)} regulations into ChromaDB")
    print(f"  Collection count: {collection.count()}")


def seed_cases():
    """导入成功案例到向量库"""
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    collection = client.get_or_create_collection(
        name="heritage_cases",
        metadata={"hnsw:space": "cosine"},
    )

    cases_data = [
        ("case_001",
         "杭州良渚古城遗址：2019年列入世界遗产名录。采用遗址+公园模式，核心遗址区严格保护，外围建设良渚文化村提供配套服务。游客动线设计为博物馆-遗址区-文创体验区，年接待游客超200万人次。投资约30亿元，回收期约12年。成功经验：严格区分核心保护区与开发区域，文创收入占总收入40%以上。",
         {"name": "良渚古城遗址", "location": "浙江杭州", "type": "古遗址"}),

        ("case_002",
         "苏州园林群：拙政园、留园等9座园林列入世界遗产。采用分散入园、限流保护策略，核心保护区内不增设商业设施，游客服务集中在园外区域。推出园林一票通串联多座园林，日均限流8000人次。年营收约2.5亿元，其中门票收入占50%，文创占30%。成功经验：以园林为核心打造全城文旅生态，而非单一景点开发。",
         {"name": "苏州园林群", "location": "江苏苏州", "type": "园林"}),

        ("case_003",
         "平遥古城：1997年列入世界遗产。采用城内保护、城外开发模式，古城内严格控制商业业态，核心保护区内禁止新建建筑。游客动线为城墙-县衙-日升昌-明清街，夜游经济为特色。年接待游客超300万人次，旅游总收入超50亿元。成功经验：保护与开发空间分离，古城整体申遗提升品牌价值。",
         {"name": "平遥古城", "location": "山西平遥", "type": "古城"}),

        ("case_004",
         "泉州开元寺：全国重点文物保护单位，采用寺内严格保护+周边文旅配套模式。寺内禁止商业活动，东西塔实行预约限流参观。周边西街改造为非遗体验街区，展示南音、提线木偶等。年游客量约150万人次，周边文创年收入约3000万元。成功经验：将寺庙保护与古城整体文旅结合，以非遗体验丰富游览内容。",
         {"name": "泉州开元寺", "location": "福建泉州", "type": "寺庙"}),
    ]

    for case_id, content, metadata in cases_data:
        collection.upsert(
            ids=[case_id],
            documents=[content],
            metadatas=[metadata],
        )

    print(f"Seeded {len(cases_data)} cases into ChromaDB")
    print(f"  Collection count: {collection.count()}")


if __name__ == "__main__":
    seed_regulations()
    seed_cases()
    print("\nDone! ChromaDB data seeded successfully.")
