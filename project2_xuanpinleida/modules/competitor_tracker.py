"""竞品追踪模块 — 监控竞品价格/Listing/评分变化"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from shared.model_router import ModelRouter


def add_competitor(
    name: str,
    asin: str = "",
    price: float = 0.0,
    rating: float = 0.0,
    reviews: int = 0,
    bsr: int = 0,
    notes: str = "",
) -> dict:
    """添加竞品"""
    return {
        "name": name,
        "asin": asin,
        "price": price,
        "rating": rating,
        "reviews": reviews,
        "bsr": bsr,
        "notes": notes,
        "added_at": "2026-07-26",
    }


def analyze_competitor_landscape(
    router: ModelRouter,
    competitors: list[dict],
    my_product: dict = None,
) -> str:
    """
    分析竞争格局，生成策略建议。
    """
    comp_summary = "\n".join(
        f"- {c['name']}: ${c.get('price', 'N/A')}, {c.get('rating', 'N/A')}★, {c.get('reviews', 'N/A')} reviews, BSR #{c.get('bsr', 'N/A')}"
        for c in competitors
    )

    my_summary = ""
    if my_product:
        my_summary = f"\nMy Product: {my_product.get('name', '')} — ${my_product.get('price', '')}, {my_product.get('rating', '')}★"

    response = router.chat_completion(
        messages=[
            {"role": "system", "content": "You are a competitive intelligence analyst for Amazon sellers. Analyze the competitor landscape and provide strategic recommendations."},
            {"role": "user", "content": f"""Analyze this competitive landscape:

COMPETITORS:
{comp_summary}
{my_summary}

Provide:
1. Overall competitive intensity assessment
2. Strengths and weaknesses of each competitor
3. Market gaps and opportunities
4. Recommended competitive strategy
5. Specific action items (pricing, positioning, differentiation)"""},
        ],
        model="qwen/qwen3.7-max",
        temperature=0.8,
    )

    return router.extract_content(response)


def detect_listing_changes(old_listing: dict, new_listing: dict) -> list[dict]:
    """检测Listing变动（模拟版）"""
    changes = []

    if old_listing.get("title") != new_listing.get("title"):
        changes.append({"type": "Title Update", "old": old_listing.get("title", ""), "new": new_listing.get("title", ""), "date": "2026-07-25"})

    if old_listing.get("price") != new_listing.get("price"):
        old_price = old_listing.get("price", 0)
        new_price = new_listing.get("price", 0)
        pct = ((new_price - old_price) / old_price * 100) if old_price else 0
        changes.append({
            "type": "Price Change",
            "old": f"${old_price:.2f}",
            "new": f"${new_price:.2f}",
            "pct": f"{pct:+.1f}%",
            "date": "2026-07-25",
        })

    if old_listing.get("bullets") != new_listing.get("bullets"):
        changes.append({"type": "Bullet Points Rewrite", "detail": "Bullet points content modified", "date": "2026-07-22"})

    if old_listing.get("images") != new_listing.get("images"):
        changes.append({"type": "Image Update", "detail": "Product images updated", "date": "2026-07-20"})

    return changes
