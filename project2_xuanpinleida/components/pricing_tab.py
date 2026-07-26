"""定价策略标签页"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from shared.model_router import ModelRouter
from modules.pricing_advisor import generate_pricing_strategy, calculate_price_elasticity


def render_pricing_tab(router: ModelRouter, config: dict):
    st.header("💲 AI定价策略助手")
    st.caption("基于竞品价格曲线和市场需求，推荐最优定价与促销策略")

    col1, col2, col3 = st.columns(3)
    with col1:
        product_name = st.text_input("产品名称", value="Bluetooth 5.3 Earbuds")
        cost = st.number_input("单位总成本 ($)", min_value=1.0, value=18.50, step=0.5,
                               help="包含采购成本 + FBA费用 + 平台佣金 + 预估广告成本")
    with col2:
        target_margin = st.slider("目标利润率", 0.10, 0.60, 0.30, 0.05, format="%.0f%%",
                                  help="期望的净利润率")
        category_avg = st.number_input("品类均价 ($)", value=49.99, step=1.0)
    with col3:
        market_demand = st.selectbox("市场需求水平", ["high", "medium", "low"],
                                     format_func=lambda x: {"high": "高需求（旺季/热门品类）", "medium": "中等需求（稳定品类）", "low": "低需求（淡季/利基品类）"}.get(x, x))

    # 竞品价格输入
    with st.expander("竞品价格数据"):
        comp_prices_text = st.text_input("竞品价格（逗号分隔）", value="39.99, 49.99, 54.99, 59.99, 29.99")
        comp_prices = [float(p.strip()) for p in comp_prices_text.split(",") if p.strip()]

    if st.button("📊 生成定价策略", type="primary", use_container_width=True):
        with st.spinner("AI正在分析市场数据，生成定价策略..."):
            # 价格弹性分析
            elasticity = calculate_price_elasticity(router, product_name, cost)

            # 完整策略
            strategy = generate_pricing_strategy(
                router=router,
                product_name=product_name,
                cost=cost,
                target_margin=target_margin,
                competitor_prices=comp_prices,
                category_avg_price=category_avg,
                market_demand=market_demand,
            )

            st.session_state["pricing_strategy"] = strategy
            st.session_state["price_elasticity"] = elasticity

        _display_pricing_results(elasticity, strategy, cost, comp_prices)

    if "price_elasticity" in st.session_state:
        st.divider()
        with st.expander("📊 上次分析结果"):
            _display_pricing_results(
                st.session_state["price_elasticity"],
                st.session_state.get("pricing_strategy", {}),
                cost,
                comp_prices if "comp_prices_text" in locals() else [],
            )


def _display_pricing_results(elasticity: list[dict], strategy: dict, cost: float, comp_prices: list[float]):
    st.subheader("📈 价格弹性分析")

    # 弹性曲线图
    df = pd.DataFrame(elasticity)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["price"], y=df["est_daily_units"], mode="lines+markers",
                             name="日销量", marker_size=12, line_width=3))
    fig.add_trace(go.Bar(x=df["price"], y=df["monthly_profit"], name="月利润",
                         marker_color="green", opacity=0.6, yaxis="y2"))
    fig.update_layout(
        height=350,
        xaxis_title="Price ($)",
        yaxis_title="Daily Units",
        yaxis2=dict(title="Monthly Profit ($)", overlaying="y", side="right"),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # 详细数据表
    st.dataframe(
        df.rename(columns={
            "price": "价格 ($)", "margin_pct": "利润率 (%)",
            "est_daily_units": "预估日销量", "daily_revenue": "日收入 ($)",
            "daily_profit": "日利润 ($)", "monthly_profit": "月利润 ($)",
        }),
        use_container_width=True,
        hide_index=True,
    )

    # 推荐价格
    recommended = [e for e in elasticity if e.get("recommended")]
    if recommended:
        rec = recommended[0]
        st.success(f"### 🎯 推荐定价: ${rec['price']:.2f} (利润率: {rec['margin_pct']:.1f}%)")
        cols = st.columns(3)
        cols[0].metric("预估月销量", f"{int(rec['est_daily_units'] * 30):,} units")
        cols[1].metric("预估月收入", f"${rec['daily_revenue'] * 30:,.2f}")
        cols[2].metric("预估月利润", f"${rec['monthly_profit']:,.2f}")

    # 竞品价格定位
    if comp_prices:
        st.subheader("📊 竞品价格定位")
        price_data = list(comp_prices) + [cost * (1 / (1 - 0.30))]  # 30%利润率的售价
        labels = [f"竞品{i+1}" for i in range(len(comp_prices))] + ["你的产品(推荐)"]
        colors = ["#95a5a6"] * len(comp_prices) + ["#2ecc71"]
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=labels, y=price_data, marker_color=colors,
                              text=[f"${p:.2f}" for p in price_data], textposition="outside"))
        fig2.update_layout(height=300, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)

    # 策略文本
    if strategy:
        st.subheader("📋 定价策略详情")
        if isinstance(strategy, dict):
            for key, value in strategy.items():
                if isinstance(value, str) and len(value) > 50:
                    with st.expander(key.replace("_", " ").title()):
                        st.markdown(value)
                elif isinstance(value, list) and len(value) > 0:
                    with st.expander(key.replace("_", " ").title()):
                        for item in value:
                            st.markdown(f"- {item}")
        else:
            st.markdown(str(strategy))
