"""智能选品标签页"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import streamlit as st
import plotly.graph_objects as go
from shared.model_router import ModelRouter
from modules.product_selector import discover_opportunities, score_opportunity


def render_selector_tab(router: ModelRouter, config: dict):
    st.header("🎯 AI智能选品引擎")
    st.caption("扫描多平台数据，发现"正在起势但尚未红海"的品类机会")

    col1, col2, col3 = st.columns(3)
    with col1:
        category = st.selectbox("一级品类", [config["category"]], disabled=True)
    with col2:
        sub_category = st.text_input("二级品类", value=config.get("sub_category", "蓝牙耳机"))
    with col3:
        market_maturity = st.selectbox(
            "市场阶段",
            ["all", "emerging", "growing", "mature"],
            format_func=lambda x: {"all": "全部", "emerging": "新兴市场", "growing": "成长期", "mature": "成熟期"}.get(x, x),
        )

    col_a, col_b = st.columns(2)
    with col_a:
        price_min = st.number_input("最低价格 ($)", min_value=1, value=10, step=5)
    with col_b:
        price_max = st.number_input("最高价格 ($)", min_value=10, value=100, step=5)

    if st.button("🔍 发现蓝海机会", type="primary", use_container_width=True):
        with st.spinner("AI正在扫描市场数据，识别蓝海机会..."):
            opportunities = discover_opportunities(
                router=router,
                category=category,
                subcategory=sub_category,
                price_range=(price_min, price_max),
                market_maturity=market_maturity,
            )

        st.session_state["opportunities"] = opportunities
        _display_opportunities(opportunities)

    # 快速演示
    if st.button("🎭 查看Demo选品结果", use_container_width=True):
        _display_demo_opportunities()

    if "opportunities" in st.session_state and st.session_state["opportunities"]:
        st.divider()
        with st.expander("📊 上次扫描结果"):
            _display_opportunities(st.session_state["opportunities"])


def _display_opportunities(opportunities: list[dict]):
    if not opportunities:
        st.warning("未发现符合条件的机会，请调整筛选条件")
        return

    st.success(f"发现 {len(opportunities)} 个潜在蓝海机会")

    for i, opp in enumerate(opportunities):
        score = opp.get("opportunity_score", 75)
        score_color = "green" if score >= 80 else ("orange" if score >= 60 else "red")

        with st.container():
            col_main, col_score = st.columns([4, 1])
            with col_main:
                st.subheader(f"#{i+1} {opp.get('niche', opp.get('name', f'Opportunity {i+1}'))}")
            with col_score:
                st.markdown(f"<h2 style='color:{score_color};text-align:center'>{score}</h2>", unsafe_allow_html=True)
                st.caption("机会评分/100")

            cols = st.columns(4)
            cols[0].metric("搜索量趋势", opp.get("search_volume", opp.get("search_volume_trend", "N/A")))
            cols[1].metric("竞争程度", opp.get("competition", opp.get("competition_level", "N/A")))
            cols[2].metric("均价", opp.get("avg_price", opp.get("average_price", "N/A")))
            cols[3].metric("进入难度", opp.get("entry_difficulty", "Medium"))

            if opp.get("strategy") or opp.get("entry_strategy"):
                st.info(f"💡 **推荐策略**: {opp.get('strategy', opp.get('entry_strategy', ''))}")
            st.divider()


def _display_demo_opportunities():
    st.divider()
    st.subheader("🎭 Demo选品结果 — 消费电子/蓝牙耳机")

    demo = [
        {"niche": "Open-Ear Air Conduction Earbuds", "opportunity_score": 87, "search_volume": "+62% MoM", "competition": "Medium", "avg_price": "$59.99", "entry_difficulty": "Moderate", "strategy": "Safety-conscious runners/cyclists underserved at $40-60 price point. Key patents expiring 2025-2026."},
        {"niche": "Kids' Volume-Limited Headphones (BLE)", "opportunity_score": 82, "search_volume": "+38% MoM", "competition": "Low", "avg_price": "$29.99", "entry_difficulty": "Easy", "strategy": "Only 3 established competitors, parents actively searching for safer alternatives. Highlight hearing protection."},
        {"niche": "Magnetic Qi2 3-in-1 Charging Stands", "opportunity_score": 78, "search_volume": "+55% MoM", "competition": "Medium-High", "avg_price": "$39.99", "entry_difficulty": "Moderate", "strategy": "Qi2 standard driving upgrade cycle. Differentiate with premium materials and travel-friendly folding design."},
        {"niche": "USB-C Retro Mechanical Numpads", "opportunity_score": 74, "search_volume": "+85% YoY", "competition": "Low", "avg_price": "$34.99", "entry_difficulty": "Easy", "strategy": "Exploding mechanical keyboard community. Zero major brands in numpad-only space. Keyboard YouTubers hungry for content."},
        {"niche": "Biodegradable Eco Phone Cases", "opportunity_score": 71, "search_volume": "+28% MoM", "competition": "Low-Medium", "avg_price": "$24.99", "entry_difficulty": "Easy", "strategy": "64% of Gen Z considers sustainability. Command 12-18% price premium with eco messaging. Low MOQ ODM solutions available."},
    ]

    for i, opp in enumerate(demo):
        score = opp["opportunity_score"]
        score_color = "green" if score >= 80 else ("orange" if score >= 60 else "red")
        with st.container():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(f"#{i+1} {opp['niche']}")
            with c2:
                st.markdown(f"<h2 style='color:{score_color};text-align:center'>{score}</h2>", unsafe_allow_html=True)
            cols = st.columns(4)
            cols[0].metric("搜索趋势", opp["search_volume"])
            cols[1].metric("竞争程度", opp["competition"])
            cols[2].metric("均价", opp["avg_price"])
            cols[3].metric("进入难度", opp["entry_difficulty"])
            st.info(f"💡 {opp['strategy']}")
            st.divider()
