"""智能选品模块 — 发现蓝海机会和品类趋势"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.model_router import ModelRouter


def discover_opportunities(
    router: ModelRouter,
    category: str,
    subcategory: str = "",
    price_range: tuple = (10, 100),
    market_maturity: str = "all",
) -> list[dict]:
    """
    扫描品类，发现蓝海机会。
    返回: list of opportunity dicts
    """
    maturity_filter = {
        "all": "all maturity levels — emerging, growing, and mature niches",
        "emerging": "only EMERGING niches — new categories with low competition and high growth potential",
        "growing": "only GROWING niches — established demand with room for new entrants",
        "mature": "only MATURE niches — saturated markets where differentiation is critical",
    }

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": "You are a product opportunity discovery expert for Amazon cross-border sellers. You identify underserved niches with high growth potential."},
            {"role": "user", "content": f"""Scan the '{category} / {subcategory}' category on Amazon. Price range: ${price_range[0]}-${price_range[1]}. Focus on {maturity_filter.get(market_maturity, maturity_filter['all'])}.

For each opportunity niche, provide:
1. Niche name and description
2. Opportunity score (0-100) based on: search volume growth, competition level, price margin potential, review gap, rating improvement opportunity
3. Search volume trend (month-over-month %)
4. Competition level (Low/Medium/High)
5. Average price point
6. Number of established competitors
7. Average competitor rating
8. Market gap: what is currently underserved
9. Recommended entry strategy
10. Estimated monthly revenue potential

Return JSON array of top 5 opportunities."""},
        ],
        model="qwen/deepseek-r1",
        temperature=0.8,
    )

    import json
    import re

    content = router.extract_content(response)
    try:
        data = json.loads(content)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, TypeError):
        match = re.search(r"\[[\s\S]*\]", content) if content else None
        return json.loads(match.group()) if match else []


def score_opportunity(
    search_volume_trend: float,
    competition_level: str,
    avg_price: float,
    review_count_avg: int,
    avg_rating: float,
) -> float:
    """
    计算机会评分（0-100）。
    """
    score = 0

    # 搜索量趋势 (25%)
    score += min(search_volume_trend / 2, 25)

    # 竞争程度 (25%) — 竞争越低分越高
    comp_score = {"low": 25, "medium": 15, "high": 5}
    score += comp_score.get(competition_level.lower(), 10)

    # 均价空间 (15%) — 有溢价空间
    if avg_price > 30:
        score += 15
    elif avg_price > 15:
        score += 10
    else:
        score += 5

    # 评论缺口 (20%) — 评论少意味着新进入者有机会
    if review_count_avg < 100:
        score += 20
    elif review_count_avg < 500:
        score += 12
    else:
        score += 5

    # 评分提升空间 (15%) — 评分低意味着可以超越
    if avg_rating < 4.0:
        score += 15
    elif avg_rating < 4.3:
        score += 10
    else:
        score += 5

    return min(score, 100)
