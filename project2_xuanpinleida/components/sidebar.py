"""项目二侧边栏组件"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import streamlit as st
from config import CATEGORIES, MARKETPLACES


def render_sidebar() -> dict:
    """渲染侧边栏，返回用户配置"""
    st.sidebar.image("https://img.icons8.com/color/96/radar-plot.png", width=64)
    st.sidebar.title("选品雷达")
    st.sidebar.caption("AI-Powered Market Intelligence")

    st.sidebar.divider()

    # API Key
    api_key = st.sidebar.text_input(
        "🔑 Model Router API Key",
        type="password",
        placeholder="留空使用Mock模式演示",
        help="初赛通过后发放的API Key",
    )

    if api_key:
        st.sidebar.success("✅ 真实API模式")
    else:
        st.sidebar.info("🔶 Mock演示模式 — 展示完整功能流程")

    st.sidebar.divider()

    # 全局筛选
    st.sidebar.subheader("🔍 全局筛选")

    main_category = st.sidebar.selectbox(
        "一级品类",
        list(CATEGORIES.keys()),
        index=0,
    )

    sub_categories = CATEGORIES.get(main_category, [])
    sub_category = st.sidebar.selectbox(
        "二级品类",
        sub_categories,
        index=0,
    )

    marketplace = st.sidebar.selectbox(
        "目标市场",
        [m["name"] for m in MARKETPLACES],
        index=0,
    )

    st.sidebar.divider()

    # 分析模型
    model = st.sidebar.selectbox(
        "🧠 分析模型",
        ["qwen/qwen3.7-max", "qwen/deepseek-r1", "qwen/deepseek-v4-pro", "qwen/qwen3.5-flash"],
        index=0,
        help="DeepSeek-R1适合深度推理分析，Qwen适合快速文案生成",
    )

    st.sidebar.divider()

    st.sidebar.caption("AI+跨境黑客松 · 初赛作品")
    st.sidebar.caption("© 2026 选品雷达 Team")

    return {
        "api_key": api_key if api_key else None,
        "model": model,
        "category": main_category,
        "sub_category": sub_category,
        "marketplace": marketplace,
    }
