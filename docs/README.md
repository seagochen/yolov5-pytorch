# IChing AI 解卦系统 - 技术文档

基于周易的 AI 智能解卦系统，结合传统易经智慧与 Google Gemini AI 技术。

## 文档目录

| 文档 | 说明 |
|------|------|
| [快速部署](01-DEPLOYMENT.md) | 环境配置与部署指南 |
| [系统架构](02-ARCHITECTURE.md) | 技术架构与设计说明 |
| [API 参考](03-API-REFERENCE.md) | 后端 API 接口文档 |
| [源码说明](04-SOURCE-CODE.md) | 各源码文件功能详解 |

## 项目概览

### 核心功能

- **随机摇卦**: 模拟三枚硬币投掷，生成六爻卦象
- **卦象计算**: 根据输入数字计算本卦、变卦
- **AI 解卦**: 基于 Gemini AI 的智能卦象解读
- **64卦数据**: 完整的周易64卦信息库

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 19 + TypeScript + Vite |
| 后端 | Python FastAPI |
| AI | Google Gemini API |
| 数据 | JSON 文件存储 |

### 项目结构

```
IChing/
├── backend/           # FastAPI 后端服务
│   ├── api/           # API 路由和端点
│   ├── services/      # 业务逻辑服务
│   ├── prompts/       # AI 提示词模板
│   ├── config/        # 配置管理
│   ├── core/          # 数据模型
│   └── main.py        # 应用入口
├── frontend/          # React 前端应用
│   └── src/
│       ├── api/       # API 客户端
│       ├── types/     # TypeScript 类型
│       ├── App.tsx    # 主组件
│       └── main.tsx   # 入口文件
├── data/              # 数据文件
│   └── gua/           # 64卦 JSON 数据
├── docs/              # 技术文档
└── gemini.json        # API Key 配置
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
