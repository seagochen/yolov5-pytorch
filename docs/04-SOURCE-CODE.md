# 源码说明

## 后端源码

### main.py

应用入口文件。

```python
# 主要功能
- 创建 FastAPI 应用实例
- 配置 CORS 中间件（允许跨域请求）
- 注册 API 路由
- 启动 uvicorn 服务器
```

关键代码：
- CORS 配置允许所有来源 (`allow_origins=["*"]`)
- 默认端口 8000

### api/router.py

API 路由聚合模块。

```python
# 路由前缀
- /api/divination  → divination 端点
- /api/interpretation → interpretation 端点
```

### api/endpoints/divination.py

占卜相关 API 端点。

| 端点 | 方法 | 功能 |
|------|------|------|
| `/calculate` | POST | 根据六个数字计算卦象 |
| `/random` | POST | 随机生成卦象 |
| `/gua/{index}` | GET | 获取指定卦象信息 |

核心逻辑：
- 调用 `GuaService` 进行卦象计算
- 加载 JSON 数据返回卦象信息

### api/endpoints/interpretation.py

AI 解卦 API 端点。

| 端点 | 方法 | 功能 |
|------|------|------|
| `/analyze` | POST | 调用 AI 分析卦象 |

核心逻辑：
- 接收卦象和问题
- 调用 `GeminiService` 生成解读

### core/models.py

Pydantic 数据模型定义。

| 模型 | 说明 |
|------|------|
| `GuaInfo` | 卦象信息 |
| `ChangingLine` | 变爻信息 |
| `DivinationRequest` | 占卜请求（含六个数字） |
| `RandomDivinationRequest` | 随机占卜请求 |
| `DivinationResponse` | 占卜响应 |
| `InterpretationRequest` | 解卦请求 |
| `InterpretationResponse` | 解卦响应 |

### services/gua_service.py

卦象计算服务，核心业务逻辑。

**主要方法**：

| 方法 | 功能 |
|------|------|
| `calculate_gua()` | 根据六个数字计算本卦、变卦 |
| `generate_random_numbers()` | 生成随机占卜数字 |
| `load_gua_data()` | 加载卦象 JSON 数据 |
| `get_changing_lines()` | 获取变爻信息 |

**计算逻辑**：

1. 六个数字（6-9）代表六爻
2. 转换规则：
   - 6 (老阴): 阴爻，变爻
   - 7 (少阳): 阳爻
   - 8 (少阴): 阴爻
   - 9 (老阳): 阳爻，变爻
3. 通过二进制计算卦序号
4. 变爻位置的爻会在变卦中翻转

### services/gemini_service.py

Gemini AI 服务封装。

**主要方法**：

| 方法 | 功能 |
|------|------|
| `interpret()` | 调用 AI 生成卦象解读 |

**实现细节**：
- 使用 `interpretation_prompts.py` 中的提示词模板
- 调用 Gemini API 生成文本
- 解析返回结果为 summary 和 interpretation

### prompts/interpretation_prompts.py

AI 提示词模板。

**系统提示词**：
- 角色设定为精通周易的道长
- 定义解读风格和格式要求

**用户提示词模板**：
- 包含占卜问题
- 本卦和变卦信息
- 变爻信息

### config/settings.py

配置管理模块。

| 配置项 | 说明 |
|--------|------|
| `PROJECT_ROOT` | 项目根目录 |
| `DATA_DIR` | 数据目录路径 |
| `GEMINI_CONFIG_PATH` | API Key 配置文件路径 |
| `GEMINI_MODEL` | 使用的 AI 模型 |

### config/gemini_client.py

Gemini 客户端管理。

- 读取 `gemini.json` 配置
- 初始化 Gemini 模型实例
- 提供全局模型访问

---

## 前端源码

### main.tsx

React 应用入口。

```tsx
// 主要功能
- 创建 React 根节点
- 渲染 App 组件
- 启用 StrictMode
```

### App.tsx

主应用组件，包含所有 UI 和逻辑。

**状态管理**：

| 状态 | 类型 | 说明 |
|------|------|------|
| `question` | string | 用户输入的问题 |
| `divinationResult` | DivinationResponse | 占卜结果 |
| `interpretation` | InterpretationResponse | AI 解读 |
| `loading` | boolean | 占卜加载状态 |
| `interpreting` | boolean | 解卦加载状态 |
| `error` | string | 错误信息 |

**主要方法**：

| 方法 | 功能 |
|------|------|
| `handleDivination()` | 执行随机占卜 |
| `handleInterpretation()` | 请求 AI 解卦 |

**UI 结构**：

```
App
├── Header (标题)
├── DivinationForm (问题输入 + 占卜按钮)
├── Error (错误提示)
└── ResultContainer
    ├── NumbersDisplay (占卜数字)
    ├── GuaDisplay (本卦 + 变卦)
    ├── ChangingLines (变爻列表)
    ├── InterpretButton (解卦按钮)
    └── InterpretationResult (AI 解读)
```

### api/client.ts

API 客户端封装。

**配置**：
- Base URL: 从环境变量 `VITE_API_URL` 读取，默认 `http://localhost:8000`
- 使用 axios 发送请求

**导出方法**：

| 方法 | 说明 |
|------|------|
| `randomDivination(request)` | 随机占卜 |
| `interpretGua(request)` | AI 解卦 |

### types/index.ts

TypeScript 类型定义。

| 类型 | 说明 |
|------|------|
| `GuaInfo` | 卦象信息接口 |
| `ChangingLine` | 变爻接口 |
| `DivinationResponse` | 占卜响应接口 |
| `RandomDivinationRequest` | 随机占卜请求接口 |
| `InterpretationRequest` | 解卦请求接口 |
| `InterpretationResponse` | 解卦响应接口 |

### App.css

组件样式文件。

主要样式：
- `.app-container`: 主容器布局
- `.gua-display`: 卦象卡片网格
- `.gua-card`: 单个卦象卡片
- `.gua-symbol`: Unicode 卦符样式
- `.interpretation-result`: AI 解读区域

### index.css

全局样式和 CSS 变量。

**颜色变量**：

```css
:root {
  --color-primary: #D4A373;   /* 主色调 */
  --color-secondary: #FEFAE0; /* 次要色 */
  --color-bg: #E9EDC9;        /* 背景色 */
  --color-text: #D4A373;      /* 文字色 */
}
```

---

## 数据文件

### data/gua/*.json

64卦数据文件，每卦一个 JSON 文件。

文件命名：`{序号}.json` (1-64)

数据结构：

```json
{
  "index": 1,
  "name": "卦名",
  "symbol": "Unicode符号",
  "description": "卦象描述",
  "judgement": "卦辞",
  "image": "象辞",
  "lines": [
    { "position": 1, "yaoci": "初爻爻辞" },
    { "position": 2, "yaoci": "二爻爻辞" },
    ...
  ]
}
```

### gemini.json

Gemini API 配置文件（需手动创建）。

```json
{
  "api_key": "YOUR_API_KEY"
}
```

> ⚠️ 此文件包含敏感信息，不应提交到版本控制。
