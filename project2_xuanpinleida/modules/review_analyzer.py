"""评论深度挖掘模块 — 分析竞品评论提取痛点和改进方向"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.model_router import ModelRouter


def analyze_reviews(
    router: ModelRouter,
    product_name: str,
    reviews_text: str = "",
    analysis_depth: str = "standard",
    target_language: str = "en",
) -> dict:
    """
    深度分析产品评论。
    返回: {"sentiment": {...}, "pain_points": [...], "feature_requests": [...], "insights": [...], "summary": "..."}
    """
    depth_config = {
        "quick": {"model": "qwen/qwen3.5-flash", "review_limit": 50},
        "standard": {"model": "qwen/qwen3.7-max", "review_limit": 200},
        "deep": {"model": "qwen/deepseek-r1", "review_limit": 500},
    }
    cfg = depth_config.get(analysis_depth, depth_config["standard"])

    system_prompt = """You are an expert product analyst specializing in cross-border e-commerce. You analyze customer reviews to extract actionable product improvement insights.

Your analysis should identify:
1. Sentiment distribution (positive/neutral/negative %)
2. Top pain points ranked by frequency × severity — these are the issues causing customer dissatisfaction
3. Feature requests — what customers explicitly asked for
4. Actionable insights — concrete product and listing improvements with estimated impact
5. Review velocity trend if temporal data is available

For each pain point and insight, you MUST provide specific, actionable recommendations that a product manager could implement.

Respond ONLY in JSON format."""

    if reviews_text:
        user_prompt = f"""Analyze the following customer reviews for: {product_name}

REVIEWS:
{reviews_text[:8000]}

Provide a comprehensive analysis. Return JSON:
{{
  "sentiment": {{"positive": 0, "neutral": 0, "negative": 0}},
  "pain_points": [{{"topic": "...", "frequency": 0, "severity": "HIGH/MEDIUM/LOW", "sample_quote": "...", "root_cause": "..."}}],
  "feature_requests": [{{"feature": "...", "mentions": 0, "priority": "HIGH/MEDIUM/LOW"}}],
  "insights": [{{"category": "...", "finding": "...", "recommendation": "...", "estimated_impact": "..."}}],
  "summary": "..."
}}"""
    else:
        user_prompt = f"Generate a comprehensive review analysis for: {product_name}"

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        model=cfg["model"],
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

    data["product_name"] = product_name
    data["analysis_depth"] = analysis_depth
    data["model_used"] = cfg["model"]
    return data


def extract_keywords_from_reviews(router: ModelRouter, reviews: list[str]) -> list[dict]:
    """从评论中提取高频关键词和关联关系"""
    # 拼接评论
    combined = "\n".join(reviews[:100])

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": "Extract the top 20 most frequently mentioned keywords/phrases from product reviews. Return JSON: [{\"keyword\": \"...\", \"count\": 0, \"sentiment\": \"positive/negative/neutral\", \"related_topics\": [...]}]"},
            {"role": "user", "content": combined[:5000]},
        ],
        model="qwen/qwen3.5-flash",
        temperature=0.3,
    )

    import json
    import re

    content = router.extract_content(response)
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        match = re.search(r"\[[\s\S]*\]", content) if content else None
        return json.loads(match.group()) if match else []
