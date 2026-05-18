"""种子数据 — 开封古建与法规初始数据

从 main.py 中提取，便于维护和扩展。
"""

from loguru import logger
from sqlalchemy import func, select


# ========== 开封古建种子数据 ==========
HERITAGE_SEED_DATA = [
    {
        "name": "铁塔", "dynasty": "宋", "building_type": "楼阁",
        "protection_level": "全国重点文物保护单位", "style": "宗教建筑",
        "province": "河南", "city": "开封", "district": "龙亭区",
        "address": "开封市龙亭区铁塔公园内",
        "longitude": 114.3538, "latitude": 34.8008,
        "description": "北宋皇佑元年(1049年)建，琉璃砖塔，高55.88米，八角十三层",
        "current_status": "保存完好", "area_size": 28000,
        "is_open": True, "ticket_price": 40.0, "annual_visitors": 500000,
    },
    {
        "name": "龙亭", "dynasty": "清", "building_type": "宫殿",
        "protection_level": "省级文物保护单位", "style": "官式建筑",
        "province": "河南", "city": "开封", "district": "龙亭区",
        "address": "开封市龙亭区中山路北段",
        "longitude": 114.3495, "latitude": 34.7993,
        "description": "清代万寿宫建筑群，位于北宋故宫遗址之上",
        "current_status": "保存完好", "area_size": 83000,
        "is_open": True, "ticket_price": 45.0, "annual_visitors": 800000,
    },
    {
        "name": "大相国寺", "dynasty": "唐", "building_type": "寺庙",
        "protection_level": "全国重点文物保护单位", "style": "宗教建筑",
        "province": "河南", "city": "开封", "district": "鼓楼区",
        "address": "开封市鼓楼区自由路西段36号",
        "longitude": 114.3458, "latitude": 34.7935,
        "description": "始建于北齐天保六年(555年)，唐宋时期著名寺院",
        "current_status": "保存完好", "area_size": 20000,
        "is_open": True, "ticket_price": 30.0, "annual_visitors": 600000,
    },
    {
        "name": "繁塔", "dynasty": "宋", "building_type": "楼阁",
        "protection_level": "全国重点文物保护单位", "style": "宗教建筑",
        "province": "河南", "city": "开封", "district": "禹王台区",
        "address": "开封市禹王台区繁塔西街30号",
        "longitude": 114.3402, "latitude": 34.7791,
        "description": "北宋太平兴国二年(977年)建，开封现存最古老的地面建筑",
        "current_status": "保存完好", "area_size": 5000,
        "is_open": True, "ticket_price": 15.0, "annual_visitors": 100000,
    },
    {
        "name": "山陕甘会馆", "dynasty": "清", "building_type": "民居",
        "protection_level": "全国重点文物保护单位", "style": "地方民居",
        "province": "河南", "city": "开封", "district": "龙亭区",
        "address": "开封市龙亭区徐府街85号",
        "longitude": 114.3488, "latitude": 34.7962,
        "description": "清代山西、陕西、甘肃三省旅汴商人集资兴建的会馆建筑",
        "current_status": "保存完好", "area_size": 3000,
        "is_open": True, "ticket_price": 25.0, "annual_visitors": 200000,
    },
    {
        "name": "延庆观", "dynasty": "元", "building_type": "寺庙",
        "protection_level": "全国重点文物保护单位", "style": "宗教建筑",
        "province": "河南", "city": "开封", "district": "鼓楼区",
        "address": "开封市鼓楼区观前街53号",
        "longitude": 114.3445, "latitude": 34.7908,
        "description": "元代道教建筑，原名重阳观，与北京白云观、四川常道观并称中国三大名观",
        "current_status": "保存完好", "area_size": 6000,
        "is_open": True, "ticket_price": 20.0, "annual_visitors": 150000,
    },
    {
        "name": "开封城墙", "dynasty": "清", "building_type": "城墙",
        "protection_level": "全国重点文物保护单位", "style": "军事建筑",
        "province": "河南", "city": "开封", "district": "全城",
        "address": "开封市环城路",
        "longitude": 114.3485, "latitude": 34.7950,
        "description": "清代重修城墙，全长14.4公里，是中国现存仅次于南京城墙的第二大古城墙",
        "current_status": "部分保存", "area_size": 80000,
        "is_open": True, "ticket_price": 0.0, "annual_visitors": 300000,
    },
    {
        "name": "包公祠", "dynasty": "现代重建", "building_type": "寺庙",
        "protection_level": "市级文物保护单位", "style": "官式建筑",
        "province": "河南", "city": "开封", "district": "鼓楼区",
        "address": "开封市鼓楼区包公湖西路12号",
        "longitude": 114.3412, "latitude": 34.7865,
        "description": "纪念北宋名臣包拯的祠堂，1984年重建于包公湖畔",
        "current_status": "保存完好", "area_size": 4000,
        "is_open": True, "ticket_price": 25.0, "annual_visitors": 400000,
    },
    {
        "name": "清明上河园", "dynasty": "现代仿建", "building_type": "园林",
        "protection_level": "未定级", "style": "园林建筑",
        "province": "河南", "city": "开封", "district": "龙亭区",
        "address": "开封市龙亭区龙亭西路5号",
        "longitude": 114.3478, "latitude": 34.8015,
        "description": "以北宋张择端《清明上河图》为蓝本建造的大型宋代文化主题公园",
        "current_status": "运营良好", "area_size": 400000,
        "is_open": True, "ticket_price": 120.0, "annual_visitors": 2000000,
    },
    {
        "name": "天波杨府", "dynasty": "现代重建", "building_type": "宫殿",
        "protection_level": "未定级", "style": "官式建筑",
        "province": "河南", "city": "开封", "district": "龙亭区",
        "address": "开封市龙亭区天波杨府路1号",
        "longitude": 114.3465, "latitude": 34.8028,
        "description": "为纪念北宋抗辽名将杨业而建，1992年重建",
        "current_status": "运营良好", "area_size": 28000,
        "is_open": True, "ticket_price": 30.0, "annual_visitors": 350000,
    },
]


# ========== 法规种子数据 ==========
REGULATION_SEED_DATA = [
    {
        "title": "中华人民共和国文物保护法",
        "source": "全国人大常委会",
        "level": "国家",
        "content": "为了加强对文物的保护，继承中华民族优秀的历史文化遗产，促进科学研究工作，进行爱国主义和革命传统教育，建设社会主义精神文明和物质文明，根据宪法，制定本法。在中华人民共和国境内，下列文物受国家保护：（一）具有历史、艺术、科学价值的古文化遗址、古墓葬、古建筑、石窟寺和石刻、壁画；（二）与重大历史事件、革命运动或者著名人物有关的以及具有重要纪念意义、教育意义或者史料价值的近代现代重要史迹、实物、代表性建筑；（三）历史上各时代珍贵的艺术品、工艺美术品；（四）历史上各时代重要的文献资料以及具有历史、艺术、科学价值的手稿和图书资料等；（五）反映历史上各时代、各民族社会制度、社会生产、社会生活的代表性实物。",
        "protection_levels": ["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"],
        "is_constraint": True,
    },
    {
        "title": "历史文化名城名镇名村保护条例",
        "source": "国务院",
        "level": "国家",
        "content": "为了加强历史文化名城、名镇、名村的保护与管理，继承中华民族优秀历史文化遗产，制定本条例。历史文化名城、名镇、名村的保护应当遵循科学规划、严格保护的原则，保持和延续其传统格局和历史风貌，维护历史文化遗产的真实性和完整性，继承和弘扬中华民族优秀传统文化，正确处理经济社会发展和历史文化遗产保护的关系。",
        "protection_levels": ["全国重点文物保护单位", "省级文物保护单位"],
        "is_constraint": True,
    },
    {
        "title": "河南省文物保护条例",
        "source": "河南省人大常委会",
        "level": "省",
        "content": "根据《中华人民共和国文物保护法》和有关法律、法规，结合本省实际，制定本条例。本省行政区域内的文物保护工作，适用本条例。各级人民政府应当重视文物保护，正确处理经济建设、社会发展与文物保护的关系，确保文物安全。基本建设、旅游开发必须遵守文物保护工作的方针，其活动不得对文物造成损害。",
        "protection_levels": ["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位", "区县级文物保护单位"],
        "is_constraint": True,
    },
    {
        "title": "开封市历史文化名城保护规划",
        "source": "开封市人民政府",
        "level": "市",
        "content": "为保护开封历史文化名城，继承优秀历史文化遗产，加强对历史文化名城保护的监督管理，促进城市经济社会发展，根据有关法律法规，结合本市实际制定。开封古城保护范围包括：城墙以内区域及城墙遗址外侧一定范围。古城保护范围内，新建、改建、扩建建筑物、构筑物，其体量、造型、色彩等应当与古城传统风貌相协调。",
        "protection_levels": ["全国重点文物保护单位", "省级文物保护单位", "市级文物保护单位"],
        "is_constraint": True,
    },
    {
        "title": "文物建筑开放导则（试行）",
        "source": "国家文物局",
        "level": "国家",
        "content": "为促进文物建筑对外开放，规范文物建筑开放工作，满足公众文化需求，根据《中华人民共和国文物保护法》等法律法规，制定本导则。文物建筑开放应当遵循最小干预原则，不得损坏文物建筑本体及附属文物，不得改变文物建筑原状。开放利用应当以文物保护为前提，坚持社会效益优先，注重发挥文物建筑的公共文化服务和社会教育功能。",
        "protection_levels": ["全国重点文物保护单位", "省级文物保护单位"],
        "is_constraint": False,
    },
]


async def seed_database(session) -> None:
    """向数据库加载种子数据（仅在表为空时执行）

    Args:
        session: SQLAlchemy async session
    """
    from app.models.heritage import Heritage, Regulation

    # 检查是否已有数据
    result = await session.scalar(select(func.count(Heritage.id)))
    if result > 0:
        logger.debug("Seed data already exists ({} heritage sites), skipping", result)
        return

    # 插入古建数据
    for h_data in HERITAGE_SEED_DATA:
        session.add(Heritage(**h_data))

    # 插入法规数据
    for r_data in REGULATION_SEED_DATA:
        session.add(Regulation(**r_data))

    await session.commit()
    logger.info("Seeded {} heritage sites and {} regulations", len(HERITAGE_SEED_DATA), len(REGULATION_SEED_DATA))
