"""市场趋势报告模块 — 生成品类趋势分析报告"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.model_router import ModelRouter


def generate_trend_report(
    router: ModelRouter,
    category: str,
    time_horizon: str = "6m",
    report_depth: str = "full",
    include_sections: list[str] = None,
) -> dict:
    """
    生成市场趋势报告。
    返回: report dict with sections
    """
    horizon_map = {
        "3m": "3 months (current quarter outlook)",
        "6m": "6 months (two quarters forward-looking)",
        "12m": "12 months (full year strategic outlook)",
    }
    depth_map = {
        "executive": "executive summary only (1-2 pages equivalent)",
        "full": "full detailed report with data and analysis",
    }

    if include_sections is None:
        include_sections = ["executive_summary", "market_size", "trends", "consumer_behavior", "regulatory", "recommendations"]

    section_instructions = {
        "executive_summary": "Executive Summary — 2-3 paragraph overview of key findings",
        "market_size": "Market Size & Growth Projections — current TAM, projected growth, CAGR, segment breakdown",
        "trends": "Emerging Trends — 5-7 key trends with confidence scores and evidence",
        "consumer_behavior": "Consumer Behavior Shifts — how buyer preferences and shopping habits are changing",
        "regulatory": "Regulatory Outlook — upcoming regulations, tariffs, compliance requirements",
        "recommendations": "Recommended Actions — prioritized, actionable strategic recommendations",
    }

    sections_str = "\n".join(
        f"- {section_instructions.get(s, s)}" for s in include_sections
    )

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": "You are a market research director specializing in cross-border e-commerce. You produce authoritative, data-driven market trend reports for Amazon sellers."},
            {"role": "user", "content": f"""Generate a {depth_map.get(report_depth, 'full')} market trend report for:

CATEGORY: {category}
TIME HORIZON: {horizon_map.get(time_horizon, '6 months')}

Include these sections:
{sections_str}

For each trend, provide:
- Signal strength (WEAK/EMERGING/STRONG/CERTAIN)
- Timeframe (NOW / 3-6 months / 6-12 months / 12+ months)
- Evidence (data points, consumer signals, industry movements)
- Impact level on cross-border sellers (HIGH/MEDIUM/LOW)
- Recommended action

Return structured JSON with each section as a key."""},
        ],
        model="qwen/deepseek-r1",
        temperature=0.7,
    )

    import json
    import re

    content = router.extract_content(response)
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        match = re.search(r"\{[\s\S]*\}", content) if content else None
        data = json.loads(match.group()) if match else {}

    data["category"] = category
    data["time_horizon"] = time_horizon
    data["generated_at"] = "2026-07-26"
    return data


def get_category_benchmarks(category: str) -> dict:
    """获取品类基准数据（模拟市场数据）"""
    benchmarks = {
        "蓝牙耳机": {
            "avg_price": 49.99, "avg_rating": 4.2, "avg_reviews": 3200,
            "cagr": 10.9, "market_size": "$35.6B", "top_competitors": 8,
            "entry_difficulty": "Medium", "margin_range": "20-35%",
            "seasonality": "Q4 peak (holiday gifting)",
        },
        "智能手表": {
            "avg_price": 89.99, "avg_rating": 4.1, "avg_reviews": 2800,
            "cagr": 8.5, "market_size": "$28.1B", "top_competitors": 6,
            "entry_difficulty": "High", "margin_range": "25-40%",
            "seasonality": "Q4+Q1 (holiday + fitness new year)",
        },
        "充电器/充电宝": {
            "avg_price": 25.99, "avg_rating": 4.3, "avg_reviews": 5100,
            "cagr": 6.2, "market_size": "$18.5B", "top_competitors": 12,
            "entry_difficulty": "Low", "margin_range": "15-25%",
            "seasonality": "Steady year-round",
        },
        "手机壳": {
            "avg_price": 15.99, "avg_rating": 4.0, "avg_reviews": 8900,
            "cagr": 4.8, "market_size": "$12.3B", "top_competitors": 20,
            "entry_difficulty": "Low", "margin_range": "30-50%",
            "seasonality": "Spike at new iPhone launch (Sep)",
        },
        "瑜伽用品": {
            "avg_price": 29.99, "avg_rating": 4.4, "avg_reviews": 1800,
            "cagr": 7.8, "market_size": "$8.2B", "top_competitors": 5,
            "entry_difficulty": "Medium", "margin_range": "25-40%",
            "seasonality": "Q1 peak (New Year fitness goals)",
        },
        "厨房用具": {
            "avg_price": 22.99, "avg_rating": 4.2, "avg_reviews": 4200,
            "cagr": 5.5, "market_size": "$22.1B", "top_competitors": 15,
            "entry_difficulty": "Medium", "margin_range": "20-35%",
            "seasonality": "Q4 peak + Mother's Day",
        },
        "宠物用品": {
            "avg_price": 18.99, "avg_rating": 4.1, "avg_reviews": 3500,
            "cagr": 9.2, "market_size": "$15.8B", "top_competitors": 10,
            "entry_difficulty": "Low-Medium", "margin_range": "25-45%",
            "seasonality": "Steady with holiday spikes",
        },
    }
    return benchmarks.get(category, {
        "avg_price": 29.99, "avg_rating": 4.1, "avg_reviews": 3000,
        "cagr": 7.0, "market_size": "$10B", "top_competitors": 10,
        "entry_difficulty": "Medium", "margin_range": "20-30%",
        "seasonality": "Steady",
    })
