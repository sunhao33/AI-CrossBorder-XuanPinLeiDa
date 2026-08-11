"""
选品雷达 — AI市场洞察平台
AI+跨境黑客松巅峰赛 · 项目二
用AI构建跨境卖家的「市场情报中心」
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from shared.model_router import ModelRouter

st.set_page_config(
    page_title="选品雷达 — AI市场洞察",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

from components.sidebar import render_sidebar
from components.review_tab import render_review_tab
from components.competitor_tab import render_competitor_tab
from components.selector_tab import render_selector_tab
from components.pricing_tab import render_pricing_tab
from components.trend_tab import render_trend_tab


def init_session():
    """初始化session state"""
    if "router" not in st.session_state:
        st.session_state.router = ModelRouter(api_key=None)
    if "competitors" not in st.session_state:
        st.session_state.competitors = []


def main():
    init_session()

    # 渲染侧边栏
    config = render_sidebar()

    # 根据API Key重新初始化router
    if config["api_key"]:
        if st.session_state.router.mock_mode or st.session_state.router.api_key != config["api_key"]:
            st.session_state.router = ModelRouter(api_key=config["api_key"])
    else:
        if not st.session_state.router.mock_mode:
            st.session_state.router = ModelRouter(api_key=None)

    router = st.session_state.router

    # 主体区域
    st.title("📡 选品雷达 — AI市场洞察平台")
    st.caption("构建跨境卖家的「市场情报中心」，将海量数据转化为可执行的选品与竞争策略 | AI+跨境黑客松巅峰赛")

    # Mock模式提示
    if router.mock_mode:
        st.info(
            "🔶 **Mock演示模式** — 所有AI分析使用模拟数据展示完整功能。"
            "在侧边栏输入Model Router API Key即可切换为真实AI分析模式。"
        )

    # 五标签页
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💬 评论分析",
        "🔭 竞品追踪",
        "🎯 智能选品",
        "💲 定价策略",
        "📈 趋势报告",
    ])

    with tab1:
        render_review_tab(router, config)

    with tab2:
        render_competitor_tab(router, config)

    with tab3:
        render_selector_tab(router, config)

    with tab4:
        render_pricing_tab(router, config)

    with tab5:
        render_trend_tab(router, config)


if __name__ == "__main__":
    main()
