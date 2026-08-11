"""市场趋势报告标签页"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import streamlit as st
import plotly.graph_objects as go
from shared.model_router import ModelRouter
from modules.trend_reporter import generate_trend_report, get_category_benchmarks


def render_trend_tab(router: ModelRouter, config: dict):
    st.header("📈 AI市场趋势报告")
    st.caption("构建跨境卖家的「市场情报中心」，将海量数据转化为可执行的选品与竞争策略")

    # 类别基准数据
    benchmarks = get_category_benchmarks(config.get("sub_category", "蓝牙耳机"))

    # KPI 卡片
    st.subheader("📊 品类基准数据")
    cols = st.columns(5)
    cols[0].metric("品类均价", f"${benchmarks['avg_price']:.2f}")
    cols[1].metric("平均评分", f"{benchmarks['avg_rating']} ★")
    cols[2].metric("平均评论数", f"{benchmarks['avg_reviews']:,}")
    cols[3].metric("年增长率", f"{benchmarks['cagr']}% CAGR")
    cols[4].metric("市场规模", benchmarks["market_size"])

    # 基准雷达图
    st.subheader("🔍 市场机会雷达图")
    categories_radar = ["增长率", "利润空间", "竞争强度(低=好)", "进入门槛(低=好)", "市场规模"]

    # 安全解析 market_size（如 "$35.6B" → 35.6 → 356）
    _ms = benchmarks["market_size"].replace("$", "").replace("B", "")
    _ms_val = int(float(_ms)) * 10

    # 安全解析 margin_range（如 "20-35%" → 70）
    _mr = benchmarks["margin_range"].split("-")[1].replace("%", "")
    _mr_val = int(_mr) * 2

    values_radar = [
        min(benchmarks["cagr"] * 8, 100),
        _mr_val,
        100 - benchmarks["top_competitors"] * 5,
        {"Low": 90, "Low-Medium": 70, "Medium": 50, "Medium-High": 30, "High": 10}.get(
            benchmarks["entry_difficulty"], 50
        ),
        min(_ms_val, 100),
    ]
    fig = go.Figure(data=go.Scatterpolar(
        r=values_radar, theta=categories_radar, fill="toself",
        name=config.get("sub_category", ""),
    ))
    fig.update_layout(height=350, margin=dict(l=40, r=40, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 趋势报告生成
    st.subheader("📝 生成趋势报告")

    col1, col2, col3 = st.columns(3)
    with col1:
        time_horizon = st.selectbox(
            "时间跨度", ["3m", "6m", "12m"],
            format_func=lambda x: {"3m": "3个月", "6m": "6个月", "12m": "12个月"}.get(x, x),
        )
    with col2:
        report_depth = st.selectbox(
            "报告深度", ["executive", "full"],
            format_func=lambda x: {"executive": "执行摘要", "full": "完整报告"}.get(x, x),
        )
    with col3:
        include_sections = st.multiselect(
            "包含章节",
            ["executive_summary", "market_size", "trends", "consumer_behavior", "regulatory", "recommendations"],
            default=["executive_summary", "trends", "recommendations"],
            format_func=lambda x: {
                "executive_summary": "执行摘要", "market_size": "市场规模",
                "trends": "新兴趋势", "consumer_behavior": "消费者洞察",
                "regulatory": "政策法规", "recommendations": "行动建议",
            }.get(x, x),
        )

    if st.button("📊 生成市场趋势报告", type="primary", use_container_width=True):
        if not include_sections:
            st.warning("请至少选择一个章节")
            return

        with st.spinner(f"AI正在综合分析{config.get('sub_category', '')}市场趋势..."):
            report = generate_trend_report(
                router=router,
                category=f"{config['category']} / {config.get('sub_category', '')}",
                time_horizon=time_horizon,
                report_depth=report_depth,
                include_sections=include_sections,
            )

        st.session_state["trend_report"] = report
        _display_report(report, include_sections)

    if st.button("🎭 查看Demo趋势报告", use_container_width=True):
        _display_demo_report()

    if "trend_report" in st.session_state:
        st.divider()
        with st.expander("📋 上次生成的报告"):
            _display_report(st.session_state["trend_report"], include_sections if include_sections else [])


def _display_report(report: dict, sections: list[str]):
    for section in sections:
        section_names = {
            "executive_summary": "📌 执行摘要",
            "market_size": "📊 市场规模与增长",
            "trends": "🔮 新兴趋势",
            "consumer_behavior": "👥 消费者行为洞察",
            "regulatory": "⚖️ 政策法规展望",
            "recommendations": "🎯 战略行动建议",
        }
        with st.expander(section_names.get(section, section)):
            content = report.get(section, "")
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            st.markdown(f"**{k}**: {v}")
                    else:
                        st.markdown(f"- {item}")
            elif isinstance(content, dict):
                for k, v in content.items():
                    st.markdown(f"**{k}**: {v}")


def _display_demo_report():
    st.divider()
    with st.expander("📌 执行摘要"):
        st.markdown("""
        **全球个人音频市场** 预计2026年达到$58.4B，增长12.4% CAGR。三大变革性趋势正在重塑竞争格局：
        1. 入耳式向开放式耳机的形态转变
        2. 欧盟USB-C强制法规（2026年12月生效）
        3. AI音频功能成为标配（实时翻译、自适应EQ）
        """)
    with st.expander("🔮 新兴趋势"):
        trends = [
            ("开放式耳机革命", "STRONG", "50% YoY增长，安全意识的消费者和空气传导技术进步推动"),
            ("USB-C强制令创造机会", "CERTAIN", "欧盟通用充电器法规2026年12月全面生效，Lightning配件市场$4.2B需全面更新"),
            ("AI音频功能主流化", "EMERGING", "实时翻译耳机、AI自适应EQ、FDA OTC助听器功能正在融合"),
            ("可持续性差异化", "GROWING", "64%的Z世代在电子产品购买中考虑可持续性，溢价12-18%"),
            ("社交电商驱动发现", "ACCELERATING", "TikTok Shop占18-34岁人群消费电子发现的22%"),
        ]
        for trend, signal, desc in trends:
            st.markdown(f"**{trend}** [{signal}]: {desc}")
    with st.expander("🎯 战略行动建议"):
        st.markdown("""
        1. **90天内推出开放式耳机** — 增长最快细分，$40-60价位仍服务不足
        2. **全产品线转USB-C** — 提前准备欧盟法规，当前即宣传"面向未来"
        3. **开发环保产品线** — 从可降解包装开始（易实现），逐步拓展到回收材料产品
        4. **投资TikTok营销** — 短视频产品演示、用户评价、"开箱体验"内容
        5. **准备欧盟数字产品护照** — 提前开始供应链文档化
        """)
