"""竞品追踪标签页"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from shared.model_router import ModelRouter
from modules.competitor_tracker import add_competitor, analyze_competitor_landscape


def render_competitor_tab(router: ModelRouter, config: dict):
    st.header("🔭 AI竞品追踪看板")
    st.caption("监控竞品价格、Listing变动、评分趋势，分析策略意图")

    # 初始化竞品列表
    if "competitors" not in st.session_state:
        st.session_state["competitors"] = [
            {"name": "SoundPro X1", "price": 49.99, "rating": 4.3, "reviews": 8421, "bsr": 847},
            {"name": "AudioMax T3", "price": 59.99, "rating": 4.5, "reviews": 12089, "bsr": 423},
            {"name": "BassBeats Pro", "price": 39.99, "rating": 4.1, "reviews": 5234, "bsr": 1523},
            {"name": "EarFit Elite", "price": 54.99, "rating": 4.6, "reviews": 3891, "bsr": 678},
        ]

    competitors = st.session_state["competitors"]

    # 竞品总览KPI
    if competitors:
        cols = st.columns(4)
        prices = [c["price"] for c in competitors]
        ratings = [c["rating"] for c in competitors]
        reviews = [c["reviews"] for c in competitors]
        bsrs = [c["bsr"] for c in competitors]

        cols[0].metric("竞品数量", len(competitors))
        cols[1].metric("价格区间", f"${min(prices):.2f} — ${max(prices):.2f}")
        cols[2].metric("平均评分", f"{sum(ratings)/len(ratings):.1f} ★")
        cols[3].metric("最低BSR", f"#{min(bsrs):,}")

    st.divider()

    # 价格对比图
    st.subheader("💰 价格对比")
    df = pd.DataFrame(competitors)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[c["name"] for c in competitors], y=[c["price"] for c in competitors],
                         marker_color=["#3498db", "#2ecc71", "#e74c3c", "#f39c12"],
                         text=[f"${c['price']:.2f}" for c in competitors], textposition="outside"))
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

    # 评分和评论对比
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("⭐ 评分对比")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=[c["name"] for c in competitors], y=[c["rating"] for c in competitors],
                              marker_color=["#3498db", "#2ecc71", "#e74c3c", "#f39c12"],
                              text=[f"{c['rating']}★" for c in competitors], textposition="outside"))
        fig2.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), yaxis_range=[3.5, 5.0])
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("📝 评论数量")
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=[c["name"] for c in competitors], y=[c["reviews"] for c in competitors],
                              marker_color=["#3498db", "#2ecc71", "#e74c3c", "#f39c12"],
                              text=[f"{c['reviews']:,}" for c in competitors], textposition="outside"))
        fig3.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    # 竞争分析按钮
    if st.button("🧠 AI竞争格局分析", type="primary", use_container_width=True):
        with st.spinner("AI正在分析竞争格局..."):
            analysis = analyze_competitor_landscape(router, competitors)
        st.markdown(analysis)

    st.divider()

    # 添加竞品
    with st.expander("➕ 添加竞品"):
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            name = st.text_input("竞品名称")
            price = st.number_input("价格 ($)", min_value=0.0, value=29.99, step=1.0)
        with col_b:
            rating = st.slider("评分", 1.0, 5.0, 4.0, 0.1)
            reviews = st.number_input("评论数", min_value=0, value=1000, step=100)
        with col_c:
            bsr = st.number_input("BSR排名", min_value=1, value=1000, step=100)
            notes = st.text_input("备注")

        if st.button("添加竞品"):
            new_comp = add_competitor(name, "", price, rating, reviews, bsr, notes)
            st.session_state["competitors"].append(new_comp)
            st.success(f"已添加 {name}")
            st.rerun()
