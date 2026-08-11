"""项目二配置：选品雷达 — AI市场洞察平台"""

CATEGORIES = {
    "消费电子": ["蓝牙耳机", "智能手表", "充电器/充电宝", "手机壳/贴膜", "电脑配件"],
    "家居用品": ["厨房用具", "收纳整理", "家纺布艺", "照明灯具", "卫浴配件"],
    "运动户外": ["健身器材", "瑜伽用品", "露营装备", "骑行配件", "运动服饰"],
    "宠物用品": ["宠物玩具", "宠物食品", "宠物服饰", "猫砂/厕所", "美容护理"],
    "美妆个护": ["护肤工具", "化妆刷具", "美甲用品", "美发工具", "口腔护理"],
}

ANALYSIS_DEPTH = {
    "quick": {"name": "快速扫描", "reviews": 50, "model": "qwen/qwen3.5-flash", "time": "~10秒"},
    "standard": {"name": "标准分析", "reviews": 200, "model": "qwen/qwen3.7-max", "time": "~40秒"},
    "deep": {"name": "深度挖掘", "reviews": 500, "model": "qwen/deepseek-r1", "time": "~2分钟"},
}

COMPETITOR_METRICS = [
    {"id": "price", "name": "价格追踪", "icon": "💰"},
    {"id": "rating", "name": "评分趋势", "icon": "⭐"},
    {"id": "reviews", "name": "评论增长", "icon": "📝"},
    {"id": "bsr", "name": "BSR排名", "icon": "📊"},
    {"id": "listing", "name": "Listing变动", "icon": "🔄"},
]

OPPORTUNITY_WEIGHTS = {
    "search_volume": 0.25,    # 搜索量趋势
    "competition": 0.25,      # 竞争程度
    "avg_price": 0.15,        # 均价空间
    "review_gap": 0.20,       # 评论数量缺口
    "rating_gap": 0.15,       # 评分提升空间
}

MARKETPLACES = [
    {"id": "us", "name": "美国 Amazon.com", "currency": "USD", "vat": False},
    {"id": "uk", "name": "英国 Amazon.co.uk", "currency": "GBP", "vat": True},
    {"id": "de", "name": "德国 Amazon.de", "currency": "EUR", "vat": True},
    {"id": "jp", "name": "日本 Amazon.co.jp", "currency": "JPY", "vat": True},
]
