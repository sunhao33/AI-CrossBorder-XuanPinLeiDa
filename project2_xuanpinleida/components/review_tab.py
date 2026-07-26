"""评论深度分析标签页"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from shared.model_router import ModelRouter
from modules.review_analyzer import analyze_reviews


def render_review_tab(router: ModelRouter, config: dict):
    st.header("💬 AI评论深度挖掘")
    st.caption("分析竞品评论，提取高频痛点，反推产品改进方向")

    col1, col2 = st.columns([2, 1])

    with col1:
        product_name = st.text_input("分析产品名称", value="SoundPro X1 Bluetooth Earbuds")

    with col2:
        analysis_depth = st.selectbox(
            "分析深度",
            ["quick", "standard", "deep"],
            format_func=lambda x: {"quick": "快速扫描 (~10秒)", "standard": "标准分析 (~40秒)", "deep": "深度挖掘 (~2分钟)"}.get(x, x),
        )

    # 评论输入选项
    input_mode = st.radio("数据来源", ["使用Mock示例数据", "粘贴评论数据"], horizontal=True)

    reviews_text = ""
    if input_mode == "粘贴评论数据":
        reviews_text = st.text_area(
            "粘贴评论（每条一行）",
            placeholder="Paste customer reviews here, one per line...",
            height=200,
        )
    else:
        st.info("📊 使用内置的蓝牙耳机产品评论数据（2,000条模拟评论）")

    if st.button("🔍 开始分析", type="primary", use_container_width=True):
        with st.spinner(f"AI正在深度分析评论数据..."):
            result = analyze_reviews(
                router=router,
                product_name=product_name,
                reviews_text=reviews_text if input_mode == "粘贴评论数据" else "",
                analysis_depth=analysis_depth,
            )

        # 存储结果
        st.session_state["review_analysis"] = result

        _display_review_analysis(result)

    # 显示缓存结果
    if "review_analysis" in st.session_state and st.session_state["review_analysis"]:
        st.divider()
        with st.expander("📊 上次分析结果"):
            _display_review_analysis(st.session_state["review_analysis"])


def _display_review_analysis(result: dict):
    """展示评论分析结果"""
    sentiment = result.get("sentiment", {})

    # 情感分布图
    st.subheader("😊 情感分布")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        fig = go.Figure(data=[go.Pie(
            labels=["Positive", "Neutral", "Negative"],
            values=[sentiment.get("positive", 62), sentiment.get("neutral", 18), sentiment.get("negative", 20)],
            marker_colors=["#2ecc71", "#f1c40f", "#e74c3c"],
            hole=0.4,
        )])
        fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # 统计指标
        m1, m2, m3 = st.columns(3)
        m1.metric("好评率", f"{sentiment.get('positive', 62)}%")
        m2.metric("中评率", f"{sentiment.get('neutral', 18)}%")
        m3.metric("差评率", f"{sentiment.get('negative', 20)}%")

    # 痛点排名
    pain_points = result.get("pain_points", [])
    if pain_points:
        st.subheader("🔴 痛点排名")
        for i, pp in enumerate(pain_points[:5]):
            severity_color = {"HIGH": "red", "MEDIUM": "orange", "LOW": "green"}
            color = severity_color.get(pp.get("severity", "").upper() if isinstance(pp.get("severity"), str) else "medium", "orange")
            with st.expander(f"#{i+1} {pp.get('topic', f'Pain Point {i+1}')} — 严重度: {pp.get('severity', 'N/A')}"):
                st.markdown(f"**频率**: {pp.get('frequency', 'N/A')}% of negative reviews")
                st.markdown(f"**典型评价**: _{pp.get('sample_quote', 'N/A')}_")
                st.markdown(f"**根因分析**: {pp.get('root_cause', 'N/A')}")

    # 特征需求
    feature_requests = result.get("feature_requests", [])
    if feature_requests:
        st.subheader("💡 用户最需要的功能")
        for fr in feature_requests[:5]:
            priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            icon = priority_icon.get(fr.get("priority", "").upper() if isinstance(fr.get("priority"), str) else "medium", "🟡")
            st.markdown(f"{icon} **{fr.get('feature', '')}** — {fr.get('mentions', 0)} 次提及")

    # 可行动建议
    insights = result.get("insights", [])
    if insights:
        st.subheader("🎯 可执行的改进建议")
        for insight in insights:
            st.markdown(f"""
            > **{insight.get('category', '')}**: {insight.get('finding', '')}
            > 💡 **建议**: {insight.get('recommendation', '')}
            > 📈 **预估影响**: {insight.get('estimated_impact', '')}
            """)

    # 摘要
    summary = result.get("summary", "")
    if summary:
        st.text_area("📋 分析摘要", summary, height=100, disabled=True)
