"""定价策略标签页"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from shared.model_router import ModelRouter
from modules.pricing_advisor import (
    calculate_price_elasticity,
    calculate_break_even,
    get_competitive_positioning,
    generate_pricing_strategy,
    generate_promotional_calendar,
)


def render_pricing_tab(router: ModelRouter, config: dict):
    st.header("💲 AI定价策略助手")
    st.caption("基于竞品价格曲线和市场需求，推荐最优定价与促销策略")

    col1, col2, col3 = st.columns(3)
    with col1:
        product_name = st.text_input("产品名称", value="Bluetooth 5.3 Earbuds")
        cost = st.number_input(
            "采购成本 ($)", min_value=1.0, value=18.50, step=0.5,
            help="产品的出厂/采购单价（不含运费）",
        )
    with col2:
        target_margin = st.slider(
            "目标利润率", 0.10, 0.60, 0.30, 0.05, format="%.0f%%",
            help="期望的净利润率",
        )
        category_avg = st.number_input("品类均价 ($)", value=49.99, step=1.0)
    with col3:
        market_demand = st.selectbox(
            "市场需求水平", ["high", "medium", "low"],
            format_func=lambda x: {
                "high": "高需求（旺季/热门品类）",
                "medium": "中等需求（稳定品类）",
                "low": "低需求（淡季/利基品类）",
            }.get(x, x),
        )

    # 竞品价格输入
    with st.expander("竞品价格数据"):
        comp_prices_text = st.text_input(
            "竞品价格（逗号分隔）", value="39.99, 49.99, 54.99, 59.99, 29.99"
        )
        try:
            comp_prices = [float(p.strip()) for p in comp_prices_text.split(",") if p.strip()]
        except ValueError:
            st.warning("价格格式有误，请使用数字并以逗号分隔")
            comp_prices = []

    if st.button("📊 生成定价策略", type="primary", use_container_width=True):
        if not comp_prices:
            st.warning("请至少输入一个竞品价格")
            return

        with st.spinner("正在计算价格弹性与盈亏分析..."):
            # 步骤1: Python 计算价格弹性（纯公式，不涉及LLM）
            elasticity = calculate_price_elasticity(
                product_name=product_name,
                cost=cost,
                demand_level=market_demand,
            )

            # 步骤2: Python 计算盈亏分析（纯公式，不涉及LLM）
            recommended = [e for e in elasticity if e.get("recommended")]
            if not recommended:
                recommended = [min(elasticity, key=lambda e: abs(e["margin_pct"] - 30))]
            rec_price = recommended[0]["price"] if recommended else elasticity[len(elasticity) // 2]["price"]

            break_even = calculate_break_even(
                cog=cost,
                price=rec_price,
            )

            # 步骤3: Python 计算竞争定位（纯公式，不涉及LLM）
            competitor_ratings = None  # 可选
            positioning = get_competitive_positioning(
                my_price=rec_price,
                my_rating=4.4,
                competitor_prices=comp_prices,
                competitor_ratings=competitor_ratings,
            )

            st.session_state["price_elasticity"] = elasticity
            st.session_state["break_even"] = break_even
            st.session_state["positioning"] = positioning

        # 显示数值计算结果
        _display_elasticity(elasticity, comp_prices)
        _display_break_even(break_even, rec_price)
        _display_positioning(positioning, comp_prices)

        # 步骤4: LLM 生成定性策略建议（基于已算好的数值）
        with st.spinner("AI正在基于计算结果生成策略建议..."):
            strategy_text = generate_pricing_strategy(
                router=router,
                product_name=product_name,
                cost=cost,
                elasticity_results=elasticity,
                break_even=break_even,
                positioning=positioning,
                competitor_prices=comp_prices,
                target_margin=target_margin,
                category_avg_price=category_avg,
                market_demand=market_demand,
            )
            st.session_state["pricing_strategy"] = strategy_text

        st.subheader("📋 AI策略建议")
        st.markdown(strategy_text)

        # 步骤5: LLM 生成促销日历
        with st.spinner("AI正在生成促销日历..."):
            promo = generate_promotional_calendar(
                router=router,
                product_name=product_name,
                base_price=rec_price,
                cost=cost,
            )
            st.session_state["promo_calendar"] = promo

        st.subheader("📅 促销日历")
        st.markdown(promo)

    # 显示缓存结果
    if "price_elasticity" in st.session_state:
        st.divider()
        with st.expander("📊 上次分析结果"):
            _display_elasticity(
                st.session_state["price_elasticity"],
                comp_prices if comp_prices else [],
            )
            if "break_even" in st.session_state:
                rec = [e for e in st.session_state["price_elasticity"] if e.get("recommended")]
                rec_p = rec[0]["price"] if rec else st.session_state["price_elasticity"][len(st.session_state["price_elasticity"]) // 2]["price"]
                _display_break_even(st.session_state["break_even"], rec_p)
            if "positioning" in st.session_state:
                _display_positioning(st.session_state["positioning"], comp_prices if comp_prices else [])
            if "pricing_strategy" in st.session_state:
                with st.expander("📋 AI策略建议"):
                    st.markdown(st.session_state["pricing_strategy"])
            if "promo_calendar" in st.session_state:
                with st.expander("📅 促销日历"):
                    st.markdown(st.session_state["promo_calendar"])


def _display_elasticity(elasticity: list[dict], comp_prices: list[float]):
    """展示价格弹性分析（纯数值结果）"""
    st.subheader("📈 价格弹性分析（公式计算）")

    df = pd.DataFrame(elasticity)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["price"], y=df["est_daily_units"], mode="lines+markers",
        name="预估日销量", marker_size=12, line_width=3, marker_color="#3498db",
    ))
    fig.add_trace(go.Bar(
        x=df["price"], y=df["monthly_profit"], name="月利润 ($)",
        marker_color="#2ecc71", opacity=0.55, yaxis="y2",
    ))
    fig.update_layout(
        height=380,
        xaxis_title="Price ($)",
        yaxis_title="Est. Daily Units",
        yaxis2=dict(title="Monthly Profit ($)", overlaying="y", side="right"),
        margin=dict(l=0, r=0, t=10, b=0),
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # 数据表
    display_df = df[["price", "margin_pct", "est_daily_units", "daily_revenue", "monthly_profit", "total_unit_cost"]].copy()
    display_df.columns = ["价格 ($)", "利润率 (%)", "预估日销量", "日收入 ($)", "月利润 ($)", "单位总成本 ($)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # 推荐价格高亮
    recommended = [e for e in elasticity if e.get("recommended")]
    if recommended:
        rec = recommended[0]
        st.success(
            f"### 🎯 推荐定价: ${rec['price']:.2f} "
            f"（利润率 {rec['margin_pct']:.1f}%，预估月利润 ${rec['monthly_profit']:,.2f}）"
        )


def _display_break_even(break_even: dict, recommended_price: float):
    """展示盈亏分析（纯数值结果）"""
    st.subheader("🧮 盈亏分析（公式计算）")

    cols = st.columns(5)
    cols[0].metric("采购成本", f"${break_even['cog']:.2f}")
    cols[1].metric("FBA费用", f"${break_even['fba_fee']:.2f}")
    cols[2].metric("平台佣金", f"${break_even['referral_fee']:.2f}")
    cols[3].metric("预估PPC/单", f"${break_even['ppc_per_unit']:.2f}")
    cols[4].metric("单位总成本", f"${break_even['total_unit_cost']:.2f}")

    cols2 = st.columns(4)
    cols2[0].metric("单位利润", f"${break_even['unit_profit']:.2f}")
    cols2[1].metric("利润率", f"{break_even['margin_pct']:.1f}%")
    cols2[2].metric("月盈亏平衡量", f"{break_even['monthly_break_even_units']:.0f} 单")
    cols2[3].metric("推荐售价", f"${recommended_price:.2f}")


def _display_positioning(positioning: dict, comp_prices: list[float]):
    """展示竞争定位（纯数值结果）"""
    st.subheader("📊 竞争价格定位")

    labels = [f"竞品{i+1}" for i in range(len(comp_prices))] + ["你的产品(推荐)"]
    prices = list(comp_prices) + [positioning["my_price"]]
    colors = ["#bdc3c7"] * len(comp_prices) + ["#2ecc71"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=prices, marker_color=colors,
        text=[f"${p:.2f}" for p in prices], textposition="outside",
    ))
    fig.add_hline(
        y=positioning["avg_competitor_price"], line_dash="dash",
        line_color="#e74c3c", annotation_text=f"竞品均价 ${positioning['avg_competitor_price']:.2f}",
    )
    fig.update_layout(height=320, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        f"定位类型: **{positioning['positioning']}** | "
        f"价格百分位: {positioning['price_percentile']:.0f}% | "
        f"竞品价格区间: ${positioning['min_competitor_price']:.2f} — ${positioning['max_competitor_price']:.2f}"
    )
