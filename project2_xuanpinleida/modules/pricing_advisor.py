"""定价策略模块 — 基于竞争和市场数据的智能定价建议"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.model_router import ModelRouter


def generate_pricing_strategy(
    router: ModelRouter,
    product_name: str,
    cost: float,
    target_margin: float = 0.30,
    competitor_prices: list[float] = None,
    category_avg_price: float = 0,
    market_demand: str = "medium",
) -> dict:
    """
    生成完整的定价策略。
    """
    comp_str = ", ".join(f"${p:.2f}" for p in (competitor_prices or []))
    demand_levels = {
        "high": "High demand — product in peak season, many buyers searching, supply may be constrained",
        "medium": "Moderate demand — steady year-round category, consistent buyer interest",
        "low": "Low demand — off-season or niche product, fewer active buyers",
    }

    system_prompt = "You are a pricing strategy expert for Amazon cross-border sellers. You optimize pricing for maximum profit while maintaining competitive positioning and sales velocity."
    user_prompt = f"""Generate a comprehensive pricing strategy for:

PRODUCT: {product_name}
UNIT COST (COGS + FBA + fees): ${cost:.2f}
TARGET MARGIN: {target_margin*100:.0f}%
COMPETITOR PRICES: {comp_str or 'N/A'}
CATEGORY AVERAGE PRICE: ${category_avg_price:.2f}
MARKET DEMAND: {demand_levels.get(market_demand, 'moderate')}

Provide:
1. Recommended base price with justification
2. Price elasticity analysis across 5 price points
3. Launch pricing strategy (first 14 days)
4. Growth phase pricing (days 15-45)
5. Maturity phase pricing (day 46+)
6. Promotional calendar with specific discount recommendations
7. Break-even analysis
8. Competitive price positioning map
9. Risk factors and contingency plans

Return structured JSON."""

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="qwen/deepseek-r1",
        temperature=0.6,
    )

    import json
    import re

    content = router.extract_content(response)
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        match = re.search(r"\{[\s\S]*\}", content) if content else None
        return json.loads(match.group()) if match else {}


def calculate_price_elasticity(
    router: ModelRouter,
    product_name: str,
    cost: float,
    price_points: list[float] = None,
) -> list[dict]:
    """
    模拟不同价位的销量和利润。
    """
    if price_points is None:
        price_points = [cost * 1.5, cost * 2.0, cost * 2.5, cost * 3.0, cost * 3.5]

    results = []
    for price in price_points:
        margin = (price - cost) / price
        price_ratio = price / cost

        # 简化的需求曲线模拟
        if price_ratio < 1.5:
            est_daily_units = 85
        elif price_ratio < 2.0:
            est_daily_units = 72
        elif price_ratio < 2.5:
            est_daily_units = 55
        elif price_ratio < 3.0:
            est_daily_units = 38
        else:
            est_daily_units = 20

        daily_revenue = est_daily_units * price
        daily_profit = est_daily_units * (price - cost)
        monthly_profit = daily_profit * 30

        results.append({
            "price": round(price, 2),
            "cost": round(cost, 2),
            "margin_pct": round(margin * 100, 1),
            "est_daily_units": est_daily_units,
            "daily_revenue": round(daily_revenue, 2),
            "daily_profit": round(daily_profit, 2),
            "monthly_profit": round(monthly_profit, 2),
            "recommended": abs(margin - 0.30) < 0.05,
        })

    return results


def generate_promotional_calendar(
    router: ModelRouter,
    product_name: str,
    base_price: float,
) -> list[dict]:
    """
    生成年度促销日历。
    """
    response = router.chat_completion(
        messages=[
            {"role": "system", "content": "You are an Amazon promotional strategy expert. Generate a promotional calendar with specific discount recommendations for each major shopping event."},
            {"role": "user", "content": f"Generate a 12-month promotional calendar for: {product_name}, base price ${base_price:.2f}. Include Prime Day, Black Friday, Cyber Monday, holiday season, and other relevant Amazon events. Return JSON array."},
        ],
        model="qwen/qwen3.7-max",
        temperature=0.7,
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
