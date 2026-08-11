# 选品雷达 — AI市场洞察平台

> AI+跨境黑客松巅峰赛 · 项目二 | 团队：SN0511

**一句话定义**：为跨境卖家打造AI驱动的"市场情报中心"，深度挖掘评论痛点、实时追踪竞品动态、智能发现蓝海机会，用数据替代直觉做决策。

---

## 项目背景

跨境卖家日常面临三大决策困境：
- ❓ **选什么品**：凭经验拍脑袋，缺乏数据支撑
- 👀 **竞品在干嘛**：靠人工每天刷页面，效率低下且容易遗漏
- 💰 **该卖多少钱**：定价靠感觉，要么卖不动要么不赚钱

**选品雷达** 用AI将海量市场数据转化为可执行的策略，让每位卖家都拥有自己的"市场情报团队"。

---

## 核心功能

| 功能 | 说明 | 调用的AI模型 |
|------|------|------------|
| 💬 评论分析 | 情感分布/痛点排名/产品改进建议 | DeepSeek-R1 + Qwen 3.7 |
| 🔭 竞品追踪 | 价格/评分/BSR监控+策略意图推断 | Qwen 3.7 Max |
| 🎯 智能选品 | 蓝海机会发现+5维机会评分 | DeepSeek-R1 |
| 💲 定价策略 | 价格弹性分析+促销日历+盈亏分析 | DeepSeek-R1 |
| 📈 趋势报告 | 品类趋势/消费者洞察/战略建议 | DeepSeek-R1 |

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动应用
cd project2_xuanpinleida
streamlit run app.py

# 3. 打开浏览器访问 http://localhost:8502
```

> **Mock模式**：无需API Key即可体验完整功能（内置蓝牙耳机品类的完整Demo数据）。在侧边栏输入Model Router API Key后自动切换为真实AI分析模式。

---

## 项目结构

```
project2_xuanpinleida/
├── app.py                      # Streamlit 主入口  
├── config.py                   # 品类/市场/分析深度配置
├── modules/                    # 业务逻辑（纯Python，可复用）
│   ├── review_analyzer.py      # 评论深度分析
│   ├── competitor_tracker.py   # 竞品追踪管理
│   ├── product_selector.py     # 蓝海机会发现
│   ├── pricing_advisor.py      # 智能定价策略
│   └── trend_reporter.py       # 市场趋势报告
├── components/                 # UI组件（Streamlit渲染层）
│   ├── sidebar.py              # 侧边栏+全局筛选
│   ├── review_tab.py           # 评论分析Dashboard
│   ├── competitor_tab.py       # 竞品追踪看板
│   ├── selector_tab.py         # 智能选品页
│   ├── pricing_tab.py          # 定价策略页
│   └── trend_tab.py            # 趋势报告页
└── shared/                     # 共享模块
    ├── model_router.py         # Model Router API 统一客户端
    └── mock_data.py            # Mock数据生成器
```

---

## 技术架构

```
┌─────────────────────────────────┐
│   Streamlit Dashboard (5 Tab)   │  ← 交互式可视化
├─────────────────────────────────┤
│   Modules (pure Python)         │  ← 业务逻辑层
│   Review / Competitor / Select  │
├─────────────────────────────────┤
│   ModelRouter (shared)          │  ← AI调用层  
│   Qwen (fast) ⇄ DeepSeek (deep) │
├─────────────────────────────────┤
│   Model Router API (126 models) │  ← 阿里云百炼
│   DeepSeek-R1 / Qwen / Kimi ... │
└─────────────────────────────────┘
```

模型调度策略：轻量任务用 Qwen 3.5 Flash（快速），综合分析用 Qwen 3.7 Max（平衡），深度推理用 DeepSeek-R1（准确）。

---

## 技术栈

- **前端**: Streamlit + Plotly（交互式图表）
- **AI**: 阿里云百炼 Model Router API
- **推理引擎**: DeepSeek-R1（市场分析、因果推断）
- **文本生成**: Qwen 3.7 Max
- **可视化**: Plotly（饼图/柱状图/折线图/雷达图/散点图）
- **语言**: Python 3.11+

---

## 比赛信息

- 赛事：AI+跨境黑客松巅峰赛
- 命题场景：AI 市场洞察
- 初赛截止：2026年8月20日
