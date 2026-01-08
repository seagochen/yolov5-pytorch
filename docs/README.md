# 易学智慧系统 - 技术文档

集成周易占卜、八字排盘、奇门遁甲的传统易学智能系统，结合 Google Gemini AI 技术提供智能解读。

## 文档目录

| 文档 | 说明 |
|------|------|
| [快速部署](01-DEPLOYMENT.md) | 环境配置与部署指南 |
| [系统架构](02-ARCHITECTURE.md) | 技术架构与设计说明（含前端组件架构、数据架构） |
| [API 参考](03-API-REFERENCE.md) | 后端 API 接口文档（含八字、奇门、指南 API） |
| [源码说明](04-SOURCE-CODE.md) | 各源码文件功能详解 |
| [用户指南](05-USER-GUIDE.md) | 面向用户的使用说明（周易、八字、奇门遁甲） |

## 项目概览

### 核心功能

#### 周易占卜
- **随机摇卦**: 模拟三枚硬币投掷，生成六爻卦象
- **卦象计算**: 根据输入数字计算本卦、变卦
- **AI 解卦**: 基于 Gemini AI 的智能卦象解读
- **64卦数据**: 完整的周易64卦信息库

#### 八字排盘
- **四柱计算**: 根据出生时间计算年月日时四柱
- **公历转农历**: 自动转换公历为农历日期
- **五行分析**: 统计五行分布，可视化展示
- **神煞判定**: 自动分析吉神凶神

#### 奇门遁甲
- **九宫排盘**: 按时间排出奇门遁甲九宫格局
- **吉凶分析**: 自动判断各宫位吉凶
- **用神对照**: 四柱用神与宫位对应关系
- **方位建议**: 提供最佳和不利方位建议

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 19 + TypeScript + Vite |
| 后端 | Python FastAPI |
| AI | Google Gemini API |
| 数据 | JSON 文件存储 |

### 项目结构

```
iching-agent/
├── backend/              # FastAPI 后端服务
│   ├── api/              # API 路由和端点
│   │   └── endpoints/    # 具体 API 端点
│   │       ├── divination.py     # 周易占卜
│   │       ├── interpretation.py # AI 解卦
│   │       ├── bazi.py          # 八字排盘
│   │       ├── qimen.py         # 奇门遁甲
│   │       └── guide.py         # 指南数据
│   ├── services/         # 业务逻辑服务
│   ├── prompts/          # AI 提示词模板
│   ├── config/           # 配置管理
│   ├── core/             # 数据模型
│   └── main.py           # 应用入口
├── frontend/             # React 前端应用
│   └── src/
│       ├── api/          # API 客户端
│       ├── components/   # React 组件
│       │   ├── DivinationTab.tsx  # 周易占卜
│       │   ├── BaziTab.tsx        # 八字排盘
│       │   └── QimenTab.tsx       # 奇门遁甲
│       ├── types/        # TypeScript 类型
│       ├── App.tsx       # 主组件（Tab 导航）
│       └── main.tsx      # 入口文件
├── data/                 # 数据文件
│   ├── gua/              # 64卦 JSON 数据
│   ├── qimen_guide.json  # 奇门遁甲指南
│   ├── bazi_guide.json   # 八字排盘指南
│   └── README.md         # 数据说明文档
├── docs/                 # 技术文档
└── gemini.json           # API Key 配置
```

## 快速开始

```bash
# 1. 配置 Gemini API Key
echo '{"api_key": "YOUR_API_KEY"}' > gemini.json

# 2. 启动后端 (端口 8000)
cd backend && pip install -r ../requirements.txt && python main.py

# 3. 启动前端 (端口 3000)
cd frontend && npm install && npm run dev
```

访问 http://localhost:3000 开始使用。

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2025-12
