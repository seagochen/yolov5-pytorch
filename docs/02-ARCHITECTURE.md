# 技术架构

本文档描述 IChing AI 解卦系统的系统架构，帮助开发者理解代码组织方式。

---

## 系统概览

```
┌─────────────────────────────────────────────────────────┐
│              前端 (React + TypeScript)                  │
│                 http://localhost:5173                   │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────▼───────────────────────────────┐
│                后端 (FastAPI)                           │
│               http://localhost:8000                     │
│  ┌───────────────────────────────────────────────────┐ │
│  │  API 端点: divination, interpretation             │ │
│  └───────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────┐ │
│  │  服务层: GuaService, GeminiService                │ │
│  └───────────────────────────────────────────────────┘ │
└────────────┬──────────────────────────┬─────────────────┘
             │                          │
     ┌───────▼───────┐          ┌───────▼───────┐
     │ Google Gemini │          │  JSON 文件     │
     │     API       │          │  (data/gua/)  │
     └───────────────┘          └───────────────┘
```

---

## 目录结构

```
IChing/
├── backend/                      # 后端代码
│   ├── api/
│   │   ├── endpoints/            # API 端点（2个模块）
│   │   │   ├── divination.py     # 占卜相关
│   │   │   └── interpretation.py # AI 解卦
│   │   └── router.py             # 路由聚合
│   │
│   ├── services/                 # 业务逻辑
│   │   ├── gua_service.py        # 卦象计算服务
│   │   └── gemini_service.py     # Gemini AI 服务
│   │
│   ├── prompts/                  # AI 提示词模板
│   │   └── interpretation_prompts.py
│   │
│   ├── core/
│   │   └── models.py             # Pydantic 数据模型
│   │
│   ├── config/
│   │   ├── settings.py           # 配置加载
│   │   └── gemini_client.py      # Gemini 客户端
│   │
│   ├── utils/                    # 工具函数
│   │
│   └── main.py                   # FastAPI 入口
│
├── frontend/                     # 前端代码
│   └── src/
│       ├── pages/                # 页面组件
│       │   └── Divination.tsx    # 主占卜页面
│       │
│       ├── components/           # 公共组件
│       │   ├── Layout.tsx        # 布局组件
│       │   ├── QuestionInput.tsx # 问题输入
│       │   ├── DivinationPanel.tsx   # 摇卦面板
│       │   ├── GuaDisplay.tsx    # 卦象显示
│       │   └── InterpretationResult.tsx  # 解卦结果
│       │
│       ├── services/
│       │   └── api.ts            # API 调用封装
│       │
│       ├── types/
│       │   └── index.ts          # TypeScript 类型
│       │
│       ├── App.tsx               # 应用入口
│       └── main.tsx              # React 入口
│
├── data/                         # 数据文件
│   └── gua/                      # 64卦 JSON 数据
│       └── *.json
│
├── gemini.json                   # API Key（需创建）
└── requirements.txt              # Python 依赖
```

---

## 后端架构

### 分层设计

```
请求 → API 端点 → 服务层 → 外部资源（Gemini/JSON文件）
         ↓
     提示词模板
```

**API 层** (`api/endpoints/`)
- 处理 HTTP 请求
- 参数验证（Pydantic）
- 调用服务层

**服务层** (`services/`)
- 业务逻辑
- 卦象计算
- AI 调用

**提示词层** (`prompts/`)
- AI 提示词模板
- 支持参数化

### 核心服务

#### GuaService

位置：`backend/services/gua_service.py`

```python
# 主要方法
yao_to_binary(yao_list, changing=False) -> str  # 爻转二进制
get_gua_info(binary) -> Dict                     # 获取卦象信息
generate_gua_image(binary) -> str                # 生成卦象图案
calculate_divination(numbers) -> Dict            # 计算占卜结果
generate_random_numbers() -> List[int]           # 随机生成摇卦数字
get_all_gua_list() -> List[Dict]                 # 获取64卦列表
get_gua_by_binary(binary) -> Dict                # 根据二进制获取卦象
```

**核心算法 - 爻转二进制**：
- 6（老阴）、8（少阴）→ 0
- 7（少阳）、9（老阳）→ 1
- 变卦时：6 → 1，9 → 0

#### GeminiService

位置：`backend/services/gemini_service.py`

```python
# 主要方法
interpret_gua(
    question: str,
    ben_gua: Dict,
    bian_gua: Dict,
    changing_lines: List[Dict]
) -> Dict[str, str]  # 返回 interpretation 和 summary

generate_response(prompt, system_instruction=None) -> str  # 通用生成
```

---

## 前端架构

### 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建**: Vite
- **样式**: TailwindCSS
- **HTTP**: Axios

### 组件结构

```
App
└── Layout
    └── Divination (主页面)
        ├── QuestionInput      # 问题输入组件
        ├── DivinationPanel    # 摇卦/手动输入面板
        ├── GuaDisplay         # 卦象显示（本卦/变卦）
        └── InterpretationResult  # AI 解卦结果
```

### 页面状态

`Divination.tsx` 管理以下状态：

```typescript
question: string              // 用户问题
divinationResult: DivinationType | null   // 占卜结果
interpretationResult: InterpretationType | null  // 解卦结果
loading: boolean              // 占卜加载状态
interpreting: boolean         // 解卦加载状态
error: string | null          // 错误信息
```

### API 封装

位置：`frontend/src/services/api.ts`

```typescript
// 占卜 API
export const divinationApi = {
  calculate: (request) => ...,   // 计算卦象
  random: (request) => ...,      // 随机摇卦
  getAllGua: () => ...,          // 获取64卦列表
  getGuaByBinary: (binary) => ...  // 查询单个卦象
};

// 解卦 API
export const interpretationApi = {
  analyze: (request) => ...      // AI 解卦
};
```

---

## 数据流

### 摇卦流程

```
用户点击摇卦 → divinationApi.random()
            → POST /api/divination/random
            → GuaService.generate_random_numbers()
            → GuaService.calculate_divination()
            → 返回本卦、变卦、变爻
```

### AI 解卦流程

```
用户点击解卦 → interpretationApi.analyze()
            → POST /api/interpretation/analyze
            → GeminiService.interpret_gua()
            → 生成解卦提示词
            → 调用 Gemini API
            → 生成总结
            → 返回解读和总结
```

---

## 数据模型

### 卦象模型

```python
class GuaInfo(BaseModel):
    name: str           # 卦名
    binary: str         # 二进制编码（6位）
    description: str    # 卦辞
    image: str          # 卦象图案
    yaoci: List[str]    # 六爻爻辞

class ChangingLine(BaseModel):
    position: int       # 爻位（1-6）
    yaoci: str          # 该爻的爻辞
```

### 请求/响应模型

```python
# 占卜请求
class DivinationRequest(BaseModel):
    numbers: List[int]  # 6个数字（6-9）
    question: str       # 占卜问题（可选）

# 占卜响应
class DivinationResponse(BaseModel):
    ben_gua: GuaInfo
    bian_gua: GuaInfo
    changing_lines: List[ChangingLine]
    question: str
    numbers: List[int]

# 解卦请求
class InterpretationRequest(BaseModel):
    question: str
    ben_gua: GuaInfo
    bian_gua: GuaInfo
    changing_lines: List[ChangingLine]

# 解卦响应
class InterpretationResponse(BaseModel):
    interpretation: str  # 详细解读
    summary: str         # 简短总结
```

---

## 配置管理

### settings.py

```python
class Settings:
    # 目录配置
    BASE_DIR = Path(...)
    GUA_DATA_DIR = DATA_DIR / "gua"
    API_KEY_FILE = BASE_DIR / "gemini.json"

    # 模型配置
    DEFAULT_MODEL = "gemini-2.0-flash"
    DEFAULT_GENERATION_CONFIG = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 2000
    }

    # CORS 配置
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        ...
    ]
```

### gemini.json

```json
{
  "api_key": "your-api-key"
}
```

**安全提示**：此文件应添加到 `.gitignore`，不要提交到版本控制。

---

## 扩展点

### 添加新的占卜方式

1. 在 `gua_service.py` 添加新的数字生成方法
2. 在 `divination.py` 添加新的 API 端点
3. 在前端 `api.ts` 添加 API 调用
4. 在 `DivinationPanel.tsx` 添加新的触发方式

### 修改 AI 解卦风格

修改 `prompts/interpretation_prompts.py` 中的：
- `SYSTEM_PROMPT`: 系统指令，定义解卦大师的角色
- `get_interpretation_prompt()`: 用户提示词模板

### 支持其他 AI 模型

修改 `config/gemini_client.py` 和 `services/gemini_service.py`，抽象 AI 接口。
