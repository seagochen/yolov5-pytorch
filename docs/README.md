# IChing AI 解卦系统文档

基于周易的 AI 智能解卦系统，结合传统易经智慧与现代 AI 技术。

---

## 文档目录

| 文档 | 说明 | 适合谁 |
|------|------|--------|
| [快速上手](01-QUICK-START.md) | 5 分钟启动应用 | 新用户 |
| [技术架构](02-ARCHITECTURE.md) | 系统设计和代码结构 | 开发者 |
| [API 参考](03-API-REFERENCE.md) | 完整的 API 文档 | 前后端开发 |
| [开发指南](04-DEVELOPMENT.md) | 修改代码的指南 | 维护者 |

---

## 快速开始

```bash
# 1. 配置 API Key
echo '{"api_key": "你的Gemini-API-Key"}' > gemini.json

# 2. 安装依赖
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 3. 启动后端
cd backend && python main.py

# 4. 启动前端（另一个终端）
cd frontend && npm run dev
```

访问 http://localhost:5173

---

## 核心功能

- **智能摇卦**: 模拟三枚硬币投掷，随机生成卦象
- **手动起卦**: 输入6个数字（6-9）计算卦象
- **AI 解卦**: 基于 Google Gemini AI 的智能卦象解读
- **64卦查询**: 浏览和查询所有64卦信息

---

## 技术栈

- **后端**: FastAPI + Google Gemini AI
- **前端**: React + TypeScript + Vite + TailwindCSS
- **存储**: JSON 文件（64卦数据）

---

## 项目结构

```
IChing/
├── backend/          # FastAPI 后端
│   ├── api/          # API 端点
│   ├── services/     # 业务逻辑
│   ├── prompts/      # AI 提示词
│   ├── config/       # 配置管理
│   └── core/         # 数据模型
├── frontend/         # React 前端
│   └── src/
│       ├── pages/        # 页面组件
│       ├── components/   # 公共组件
│       ├── services/     # API 调用
│       └── types/        # TypeScript 类型
├── data/             # 数据文件
│   └── gua/          # 64卦 JSON 数据
├── docs/             # 文档（你在这里）
└── gemini.json       # API Key（需创建）
```

---

## 常用链接

- 前端界面: http://localhost:5173
- API 文档: http://localhost:8000/docs
- 后端 API: http://localhost:8000/api

---

**版本**: 1.0.0
**更新**: 2025-12-02
