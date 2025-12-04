# 系统架构

## 整体架构

```
┌─────────────────┐     HTTP/REST     ┌─────────────────┐     API      ┌─────────────────┐
│                 │ ◄───────────────► │                 │ ◄──────────► │                 │
│  React 前端     │                   │  FastAPI 后端   │              │  Gemini AI      │
│  (TypeScript)   │                   │  (Python)       │              │  (Google)       │
│                 │                   │                 │              │                 │
└─────────────────┘                   └────────┬────────┘              └─────────────────┘
                                               │
                                               ▼
                                      ┌─────────────────┐
                                      │                 │
                                      │  64卦 JSON 数据 │
                                      │  (data/gua/)    │
                                      │                 │
                                      └─────────────────┘
```

## 后端架构

### 分层设计

```
backend/
├── main.py              # 应用入口，CORS 配置
├── api/                 # API 层
│   ├── router.py        # 路由聚合
│   └── endpoints/       # 具体端点
│       ├── divination.py    # 占卜相关 API
│       └── interpretation.py # AI 解卦 API
├── services/            # 业务逻辑层
│   ├── gua_service.py       # 卦象计算服务
│   └── gemini_service.py    # AI 服务
├── core/                # 核心模块
│   └── models.py            # 数据模型
├── config/              # 配置模块
│   ├── settings.py          # 配置管理
│   └── gemini_client.py     # Gemini 客户端
└── prompts/             # AI 提示词
    └── interpretation_prompts.py
```

### 数据流

1. **占卜流程**
   ```
   用户请求 → API 端点 → GuaService 计算卦象 → 加载 JSON 数据 → 返回结果
   ```

2. **AI 解卦流程**
   ```
   占卜结果 + 问题 → API 端点 → GeminiService → 构建 Prompt → 调用 AI → 返回解读
   ```

## 前端架构

### 组件结构

```
frontend/src/
├── main.tsx         # 应用入口
├── App.tsx          # 主组件（状态管理 + UI）
├── api/
│   └── client.ts    # API 客户端封装
├── types/
│   └── index.ts     # TypeScript 类型定义
├── App.css          # 组件样式
└── index.css        # 全局样式
```

### 状态管理

使用 React useState 管理本地状态：

- `question`: 用户输入的问题
- `divinationResult`: 占卜结果
- `interpretation`: AI 解读结果
- `loading` / `interpreting`: 加载状态
- `error`: 错误信息

## 卦象计算逻辑

### 数字转卦象

1. 六个数字（6-9）表示六爻
2. 每个数字含义：
   - 6: 老阴（变爻）
   - 7: 少阳
   - 8: 少阴
   - 9: 老阳（变爻）

3. 转换为二进制：
   - 阳爻 (7, 9) → 1
   - 阴爻 (6, 8) → 0

4. 计算本卦和变卦的卦序号

### 随机占卜

模拟三枚硬币投掷：
- 随机生成 6 个数字（6-9）
- 根据数字计算卦象

## 数据存储

### 64卦数据结构

每卦数据存储在 `data/gua/{序号}.json`：

```json
{
  "index": 1,
  "name": "乾",
  "symbol": "䷀",
  "description": "乾为天",
  "judgement": "元亨利贞",
  "image": "天行健，君子以自强不息",
  "lines": [
    {
      "position": 1,
      "yaoci": "初九：潜龙勿用"
    }
  ]
}
```

## API 设计

### RESTful 规范

- `POST /api/divination/calculate`: 根据数字计算卦象
- `POST /api/divination/random`: 随机占卜
- `GET /api/divination/gua/{index}`: 获取卦象信息
- `POST /api/interpretation/analyze`: AI 解卦

详见 [API 参考](03-API-REFERENCE.md)。
