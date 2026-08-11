"""定价策略模块 — 数值计算走公式/算法，LLM只负责定性策略分析"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.model_router import ModelRouter


# ═══════════════════════════════════════════════════════
# 纯 Python 数值计算（不依赖 LLM，保证精度可靠）
# ═══════════════════════════════════════════════════════

def estimate_fba_fee(price: float, weight_oz: float = 5.0, size_tier: str = "standard") -> float:
    """估算 FBA 费用（基于 Amazon 2026 费率表）"""
    if size_tier == "standard":
        fulfillment = 3.22 if weight_oz <= 4 else 3.22 + 0.08 * (weight_oz - 4)
        storage_monthly = 0.83 * (weight_oz / 16)  # cubic ft 估算
        return round(fulfillment + storage_monthly, 2)
    elif size_tier == "oversize":
        fulfillment = 5.90 + 0.08 * max(weight_oz - 12, 0)
        storage_monthly = 1.20 * (weight_oz / 16)
        return round(fulfillment + storage_monthly, 2)
    else:
        return round(3.22 + 0.08 * max(weight_oz - 4, 0), 2)


def estimate_referral_fee(price: float, category: str = "consumer_electronics") -> float:
    """估算平台佣金（Amazon 各类目费率）"""
    rates = {
        "consumer_electronics": 0.15,
        "accessories": 0.15,
        "home_kitchen": 0.15,
        "sports_outdoors": 0.15,
        "pet_supplies": 0.15,
        "beauty": 0.15,
        "clothing": 0.17,
    }
    rate = rates.get(category, 0.15)
    return round(price * rate, 2)


def calculate_break_even(
    cog: float,
    price: float,
    fba_fee: float = None,
    referral_fee: float = None,
    ppc_per_unit: float = None,
    category: str = "consumer_electronics",
    weight_oz: float = 5.0,
) -> dict:
    """
    计算盈亏分析 — 纯公式计算，不涉及 LLM。
    """
    if fba_fee is None:
        fba_fee = estimate_fba_fee(price, weight_oz)
    if referral_fee is None:
        referral_fee = estimate_referral_fee(price, category)
    if ppc_per_unit is None:
        ppc_per_unit = price * 0.10  # 默认 PPC 占售价 10%

    total_cost = cog + fba_fee + referral_fee + ppc_per_unit
    unit_profit = price - total_cost
    margin = unit_profit / price if price > 0 else 0
    monthly_break_even_units = (cog * 200) / unit_profit if unit_profit > 0 else float("inf")

    return {
        "cog": round(cog, 2),
        "fba_fee": round(fba_fee, 2),
        "referral_fee": round(referral_fee, 2),
        "ppc_per_unit": round(ppc_per_unit, 2),
        "total_unit_cost": round(total_cost, 2),
        "unit_profit": round(unit_profit, 2),
        "margin_pct": round(margin * 100, 1),
        "monthly_break_even_units": round(monthly_break_even_units, 0),
    }


def calculate_price_elasticity(
    product_name: str = "",
    cost: float = 0,
    price_points: list[float] = None,
    category: str = "consumer_electronics",
    weight_oz: float = 5.0,
    demand_level: str = "medium",
) -> list[dict]:
    """
    价格弹性模拟 — 纯算法计算，不依赖 LLM。
    使用线性需求曲线 + 需求弹性系数模拟不同价位的销量和利润。
    """
    if price_points is None:
        multiplier = 1.0
        if cost < 10:
            multiplier = 3.5
        elif cost < 20:
            multiplier = 2.8
        elif cost < 40:
            multiplier = 2.2
        else:
            multiplier = 1.8
        base_price = round(cost * multiplier / 5) * 5
        price_points = sorted([
            round(base_price * 0.60 / 5) * 5,
            round(base_price * 0.82 / 5) * 5,
            round(base_price * 1.00 / 5) * 5,
            round(base_price * 1.18 / 5) * 5,
            round(base_price * 1.35 / 5) * 5,
        ])

    # 需求弹性系数
    demand_multipliers = {
        "high": {"base_units": 100, "elasticity": 1.8},
        "medium": {"base_units": 65, "elasticity": 1.5},
        "low": {"base_units": 35, "elasticity": 1.2},
    }
    dm = demand_multipliers.get(demand_level, demand_multipliers["medium"])
    base_units = dm["base_units"]
    elasticity = dm["elasticity"]

    # 以中间价位为基准
    mid_price = sorted(price_points)[len(price_points) // 2]

    results = []
    for price in price_points:
        # 价格越高销量越低（需求定律）
        price_ratio = price / mid_price if mid_price > 0 else 1
        est_daily_units = max(5, round(base_units / (price_ratio ** elasticity)))

        fba_fee = estimate_fba_fee(price, weight_oz)
        referral_fee = estimate_referral_fee(price, category)
        ppc = round(price * 0.10, 2)

        total_unit_cost = cost + fba_fee + referral_fee + ppc
        unit_profit = price - total_unit_cost
        margin = unit_profit / price if price > 0 else 0

        daily_revenue = round(est_daily_units * price, 2)
        daily_profit = round(est_daily_units * unit_profit, 2)
        monthly_profit = round(daily_profit * 30, 2)

        results.append({
            "price": round(price, 2),
            "cost": round(cost, 2),
            "fba_fee": round(fba_fee, 2),
            "referral_fee": round(referral_fee, 2),
            "ppc_per_unit": ppc,
            "total_unit_cost": round(total_unit_cost, 2),
            "unit_profit": round(unit_profit, 2),
            "margin_pct": round(margin * 100, 1),
            "est_daily_units": est_daily_units,
            "daily_revenue": daily_revenue,
            "daily_profit": daily_profit,
            "monthly_profit": monthly_profit,
            "recommended": abs(margin - 0.30) < 0.06,
        })

    return results


def get_competitive_positioning(
    my_price: float,
    my_rating: float,
    competitor_prices: list[float],
    competitor_ratings: list[float] = None,
) -> dict:
    """
    竞争定位分析 — 纯算法计算价格和评分在市场中的相对位置。
    """
    all_prices = competitor_prices + [my_price]
    avg_comp_price = sum(competitor_prices) / len(competitor_prices) if competitor_prices else my_price
    min_comp_price = min(competitor_prices) if competitor_prices else my_price
    max_comp_price = max(competitor_prices) if competitor_prices else my_price

    price_percentile = sum(1 for p in sorted(all_prices) if p <= my_price) / len(all_prices) * 100

    # 定位分类
    if my_price <= min_comp_price * 1.05:
        positioning = "Budget"
    elif my_price >= max_comp_price * 0.95:
        positioning = "Premium"
    elif my_price <= avg_comp_price:
        positioning = "Value"
    else:
        positioning = "Premium-Value"

    return {
        "positioning": positioning,
        "my_price": round(my_price, 2),
        "avg_competitor_price": round(avg_comp_price, 2),
        "min_competitor_price": round(min_comp_price, 2),
        "max_competitor_price": round(max_comp_price, 2),
        "price_percentile": round(price_percentile, 1),
        "competitor_count": len(competitor_prices),
    }


# ═══════════════════════════════════════════════════════
# LLM 定性策略分析（数值数据已由 Python 算好）
# ═══════════════════════════════════════════════════════

def generate_pricing_strategy(
    router: ModelRouter,
    product_name: str,
    cost: float,
    elasticity_results: list[dict],
    break_even: dict,
    positioning: dict,
    competitor_prices: list[float] = None,
    target_margin: float = 0.30,
    category_avg_price: float = 0,
    market_demand: str = "medium",
    target_market: str = "US",
) -> str:
    """
    生成定价策略建议 — LLM 只做定性分析和文字策略，所有数值由 Python 预先算好传入。
    """

    # 找到推荐价位
    recommended = [e for e in elasticity_results if e.get("recommended")]
    if not recommended:
        # 找利润率最接近30%的
        recommended = [min(elasticity_results, key=lambda e: abs(e["margin_pct"] - 30))]
    rec = recommended[0] if recommended else elasticity_results[len(elasticity_results) // 2]

    demand_labels = {
        "high": "高需求（旺季/热门品类）— 搜索量高、转化率高、买家购买意愿强",
        "medium": "中等需求（稳定品类）— 全年需求平稳、竞争格局相对固定",
        "low": "低需求（淡季/利基品类）— 搜索量低、需要精准定位目标客群",
    }

    price_table = "\n".join(
        f"| ${e['price']:.2f} | {e['est_daily_units']} 单/天 | ${e['monthly_profit']:,.2f} | {e['margin_pct']:.1f}% |"
        f"{' ★推荐' if e.get('recommended') else ''}"
        for e in elasticity_results
    )

    comp_prices_str = ", ".join(f"${p:.2f}" for p in (competitor_prices or []))

    # LLM 只看到结构化的计算结果，不做任何数值运算
    system_prompt = """You are a pricing strategy expert for Amazon cross-border sellers.
You receive pre-computed numerical data (price elasticity, break-even, competitive positioning)
and your job is to provide QUALITATIVE strategy recommendations ONLY.

CRITICAL RULES:
- NEVER re-compute, override, or question the numerical data provided. Trust the computed numbers.
- NEVER generate new price points, revenue figures, or margin percentages.
- Focus ONLY on: launch timing strategy, promotional tactics, competitive narrative,
  risk factors, and actionable business recommendations.
- Keep responses concise and tactical."""

    user_prompt = f"""Generate a qualitative pricing strategy based on these PRE-COMPUTED results:

PRODUCT: {product_name}
TARGET MARKET: {target_market}
MARKET DEMAND: {demand_labels.get(market_demand, 'moderate')}
CATEGORY AVERAGE PRICE: ${category_avg_price:.2f}
COMPETITOR PRICES: {comp_prices_str or 'N/A'}

=== COMPUTED ELASTICITY TABLE (DO NOT RE-CALCULATE) ===
| Price | Est. Daily Units | Monthly Profit | Margin |
|-------|-----------------|---------------|--------|
{price_table}

=== RECOMMENDED PRICE POINT: ${rec['price']:.2f} (margin {rec['margin_pct']:.1f}%) ===

=== BREAK-EVEN ANALYSIS ===
- Total unit cost: ${break_even['total_unit_cost']:.2f}
- Unit profit at recommended price: ${break_even['unit_profit']:.2f}
- Monthly break-even volume: {break_even['monthly_break_even_units']:.0f} units

=== COMPETITIVE POSITIONING ===
- Your positioning tier: {positioning['positioning']}
- Avg competitor price: ${positioning['avg_competitor_price']:.2f}
- Price range in market: ${positioning['min_competitor_price']:.2f} — ${positioning['max_competitor_price']:.2f}
- Your price is at the {positioning['price_percentile']:.0f}th percentile

Based on the above COMPUTED data, provide:
1. Launch phase strategy (first 14 days) — specific promotional tactics
2. Growth phase strategy (days 15-45) — how to transition pricing
3. Maturity phase strategy (day 46+) — long-term pricing approach
4. Key promotional events to plan for (2-4 events with suggested discount range)
5. Competitive narrative — how to position against competitors
6. 2-3 risk factors and contingency plans

Respond in Markdown. Do NOT generate any new numerical data."""

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="qwen/qwen3.7-max",
        temperature=0.6,
    )

    return router.extract_content(response)


def generate_promotional_calendar(
    router: ModelRouter,
    product_name: str,
    base_price: float,
    cost: float,
    target_market: str = "US",
) -> str:
    """
    生成促销日历 — LLM 做定性规划，价格/折扣由提示词给定。
    """
    system_prompt = """You are an Amazon promotional strategy expert.
Generate a promotional calendar with timing and tactics.
Use ONLY the discount ranges provided — do not invent new numbers."""

    user_prompt = f"""Generate a 12-month promotional calendar for:
- Product: {product_name}
- Base price: ${base_price:.2f}
- Unit cost: ${cost:.2f} (minimum viable discount floor: {(1 - cost/base_price)*100:.0f}% max discount)
- Target market: {target_market}

For each event, specify: month, event name, promotion type (Lightning Deal / Coupon / Deal of the Day / Bundle),
recommended discount range, and expected impact (qualitative — high/medium/low volume uplift).

Important Amazon events to consider: Prime Day (Jul), Back to School (Aug-Sep), Prime Fall Deal (Oct),
Black Friday (Nov), Cyber Monday (Nov), Holiday Season (Dec), New Year Fitness (Jan), Valentine's (Feb),
Spring Sale (Mar), Mother's Day (May), Father's Day (Jun).

Return as Markdown table."""

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model="qwen/qwen3.7-max",
        temperature=0.7,
    )

    return router.extract_content(response)
