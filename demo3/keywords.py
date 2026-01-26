# -*- coding: utf-8 -*-
"""
NMPA医疗器械数据采集 - 关键词配置
"""

# 需要爬取的产品列表（原始信息）
PRODUCTS = [
    {
        "id": 1,
        "short_name": "Gastro Panel(4-in-1)",
        "english_name": "Rotavirus / Adenovirus / Norovirus / Astrovirus Combo Rapid Test Cassette",
        "chinese_name": "轮状病毒/腺病毒/诺如病毒/星状病毒联合检测试剂盒(胶体金法)",
        "sample_type": "Feces(粪便)",
    },
    {
        "id": 2,
        "short_name": "FOB + Tf(Combo)",
        "english_name": "FOB (Hemoglobin)/ Transferrin Combo Rapid Test Cassette",
        "chinese_name": "便隐血(血红蛋白)/转铁蛋白联合检测",
        "sample_type": "Feces(粪便)",
    },
    {
        "id": 3,
        "short_name": "H.pylori Ag",
        "english_name": "H.pylori Antigen Rapid Test Cassette",
        "chinese_name": "幽门螺杆菌抗原检测试剂盒",
        "sample_type": "Feces(粪便)",
    },
    {
        "id": 4,
        "short_name": "Syphilis (TP)",
        "english_name": "Syphilis (TP) Antibody Rapid Test Cassette",
        "chinese_name": "梅毒螺旋体抗体检测试剂盒",
        "sample_type": "Serum/Plasma/Whole Blood (血清/血浆/全血)",
    },
]

# 搜索关键词配置（product_id 对应 PRODUCTS 中的 id）
SEARCH_KEYWORDS = [
    # 产品1: 轮状病毒/腺病毒/诺如病毒/星状病毒
    {"keyword": "轮状病毒", "product_id": 1},
    {"keyword": "腺病毒", "product_id": 1},
    {"keyword": "诺如病毒", "product_id": 1},
    {"keyword": "星状病毒", "product_id": 1},
    {"keyword": "Rotavirus", "product_id": 1},
    {"keyword": "Adenovirus", "product_id": 1},
    {"keyword": "Norovirus", "product_id": 1},
    {"keyword": "Astrovirus", "product_id": 1},
    # 产品2: 便隐血/转铁蛋白
    {"keyword": "便隐血", "product_id": 2},
    {"keyword": "转铁蛋白", "product_id": 2},
    {"keyword": "血红蛋白", "product_id": 2},
    {"keyword": "FOB", "product_id": 2},
    {"keyword": "Transferrin", "product_id": 2},
    # 产品3: 幽门螺杆菌
    {"keyword": "幽门螺杆菌", "product_id": 3},
    {"keyword": "H.pylori", "product_id": 3},
    # 产品4: 梅毒螺旋体
    {"keyword": "梅毒螺旋体", "product_id": 4},
    {"keyword": "Syphilis", "product_id": 4},
]

# 筛选条件配置（product_id 对应 PRODUCTS 中的 id）
FILTER_RULES = [
    {
        "product_id": 1,
        # 产品名称包含"检测试剂盒"且包含"胶体金法"
        "must_contain_all": ["检测试剂盒", "胶体金法"],
    },
    {
        "product_id": 2,
        # 同时包含（便隐血/血红蛋白/FOB）AND（转铁蛋白/Transferrin）
        "must_contain_one_from_each": [
            ["便隐血", "血红蛋白", "FOB"],
            ["转铁蛋白", "Transferrin"],
        ],
    },
    {
        "product_id": 3,
        # 产品名称包含"抗原"且包含"检测试剂盒"
        "must_contain_all": ["抗原", "检测试剂盒"],
    },
    {
        "product_id": 4,
        # 产品名称包含"抗体"且包含"检测试剂盒"
        "must_contain_all": ["抗体", "检测试剂盒"],
    },
]

# 所有搜索关键词列表（方便遍历）
ALL_KEYWORDS = [item["keyword"] for item in SEARCH_KEYWORDS]


def get_product_id_by_keyword(keyword):
    """根据搜索关键词获取产品ID"""
    for item in SEARCH_KEYWORDS:
        if item["keyword"] == keyword:
            return item["product_id"]
    return None


def get_filter_rule_by_product_id(product_id):
    """根据产品ID获取筛选规则"""
    for rule in FILTER_RULES:
        if rule["product_id"] == product_id:
            return rule
    return None


def filter_product(product_name, search_keyword):
    """
    根据搜索关键词和产品名称判断是否符合筛选条件
    如果产品名称包含"..."，直接保留（名称被截断，需要后续获取详情）
    """
    # 名称被截断，直接保留
    if "..." in product_name:
        return True

    product_id = get_product_id_by_keyword(search_keyword)
    if not product_id:
        return False

    rule = get_filter_rule_by_product_id(product_id)
    if not rule:
        return False

    # 条件1：必须同时包含所有关键词
    must_contain_all = rule.get("must_contain_all", [])
    if must_contain_all:
        for kw in must_contain_all:
            if kw not in product_name:
                return False

    # 条件2：必须从每组中至少包含一个
    must_contain_one_from_each = rule.get("must_contain_one_from_each", [])
    if must_contain_one_from_each:
        for group in must_contain_one_from_each:
            found = False
            for kw in group:
                if kw in product_name:
                    found = True
                    break
            if not found:
                return False

    return True
