# 开发指南

本文档帮助你理解代码结构，快速定位和修改代码。

---

## 快速定位

### 按功能查找文件

| 需求 | 后端文件 | 前端文件 |
|------|---------|---------|
| 占卜计算 | `api/endpoints/divination.py` | `pages/Divination.tsx` |
| AI 解卦 | `api/endpoints/interpretation.py` | `pages/Divination.tsx` |
| 卦象服务 | `services/gua_service.py` | - |
| Gemini 调用 | `services/gemini_service.py` | - |
| API 调用封装 | - | `services/api.ts` |

### 按类型查找文件

| 类型 | 文件位置 |
|------|---------|
| API 路由 | `backend/api/endpoints/*.py` |
| 数据模型 | `backend/core/models.py` |
| 业务逻辑 | `backend/services/*.py` |
| AI 提示词 | `backend/prompts/*.py` |
| 配置加载 | `backend/config/settings.py` |
| 前端页面 | `frontend/src/pages/*.tsx` |
| 前端组件 | `frontend/src/components/*.tsx` |
| 前端 API | `frontend/src/services/api.ts` |
| 前端类型 | `frontend/src/types/index.ts` |

---

## 常见修改场景

### 场景 1：修改 AI 解卦提示词

提示词决定 AI 的输出质量，是最常见的调整需求。

**文件位置**: `backend/prompts/interpretation_prompts.py`

| 内容 | 说明 |
|------|------|
| `SYSTEM_PROMPT` | 系统指令，定义解卦大师角色 |
| `get_interpretation_prompt()` | 用户提示词模板 |
| `get_summary_prompt()` | 生成总结的提示词 |

**修改示例**：调整解卦风格

```python
# backend/prompts/interpretation_prompts.py

SYSTEM_PROMPT = """你是一位精通周易的解卦大师，拥有深厚的易经知识。
请根据用户的问题和所得卦象，给出详细、有洞察力的解读。

解卦时请遵循以下结构：
1. 【卦象概述】简要介绍本卦的基本含义
2. 【针对问题的解读】结合用户的具体问题分析
3. 【变爻分析】如有变爻，解释变爻的特殊意义
4. 【变卦趋势】分析变卦代表的发展趋势
5. 【综合建议】给出实际可行的建议

注意：用通俗语言解释，避免过于绝对的断言。"""
```

### 场景 2：添加新的 API 端点

**完整步骤**:

#### 步骤 1：定义数据模型

```python
# backend/core/models.py

class MyNewRequest(BaseModel):
    param1: str
    param2: Optional[int] = None

class MyNewResponse(BaseModel):
    result: str
    details: dict
```

#### 步骤 2：创建 API 端点

```python
# backend/api/endpoints/my_feature.py

from fastapi import APIRouter, HTTPException
from ...core.models import MyNewRequest, MyNewResponse

router = APIRouter()

@router.post("/", response_model=MyNewResponse)
async def my_function(request: MyNewRequest):
    # 业务逻辑
    return MyNewResponse(result="ok", details={})
```

#### 步骤 3：注册路由

```python
# backend/api/router.py

from .endpoints import my_feature

api_router.include_router(
    my_feature.router,
    prefix="/my_feature",
    tags=["my_feature"]
)
```

#### 步骤 4：前端 API 调用

```typescript
// frontend/src/services/api.ts

export const myFeatureApi = {
  doSomething: async (request: MyNewRequest): Promise<MyNewResponse> => {
    const response = await api.post<MyNewResponse>('/my_feature/', request);
    return response.data;
  },
};
```

#### 步骤 5：前端类型定义

```typescript
// frontend/src/types/index.ts

export interface MyNewRequest {
  param1: string;
  param2?: number;
}

export interface MyNewResponse {
  result: string;
  details: Record<string, any>;
}
```

### 场景 3：修改前端组件

**文件位置**: `frontend/src/components/`

| 组件 | 功能 |
|------|------|
| `QuestionInput.tsx` | 问题输入框 |
| `DivinationPanel.tsx` | 摇卦/手动输入面板 |
| `GuaDisplay.tsx` | 卦象显示 |
| `InterpretationResult.tsx` | 解卦结果展示 |
| `Layout.tsx` | 页面布局 |

**修改样式**: 使用 TailwindCSS 类名直接在组件中修改。

### 场景 4：添加新的卦象数据

**文件位置**: `data/gua/*.json`

**JSON 格式**:
```json
{
  "111111": {
    "name": "乾",
    "alternate_name": "乾为天",
    "description": "元亨利贞。",
    "yaoci": [
      "初九：潜龙勿用。",
      "九二：见龙在田，利见大人。",
      "九三：君子终日乾乾，夕惕若厉，无咎。",
      "九四：或跃在渊，无咎。",
      "九五：飞龙在天，利见大人。",
      "上九：亢龙有悔。"
    ]
  }
}
```

**键说明**:
- 键名为6位二进制字符串
- `name`: 卦名
- `alternate_name`: 别名
- `description`: 卦辞
- `yaoci`: 六爻爻辞数组（从初爻到上爻）

### 场景 5：修改配置

**配置文件**: `backend/config/settings.py`

```python
class Settings:
    # 修改默认模型
    DEFAULT_MODEL = "gemini-2.0-flash"

    # 修改生成参数
    DEFAULT_GENERATION_CONFIG = {
        "temperature": 0.7,      # 创造性（0-1）
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 2000
    }
```

---

## 调试技巧

### 后端调试

```bash
# 启动带热重载的后端
cd backend
uvicorn main:app --reload --port 8000

# 或直接运行
python main.py
```

**在代码中添加日志**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info(f"Processing request: {request}")
logger.error(f"Error: {e}")
```

### 前端调试

```bash
# 启动开发服务器
cd frontend
npm run dev
```

- 打开浏览器开发者工具 (F12)
- Network 标签查看 API 请求
- Console 标签查看错误信息

**在代码中添加日志**:
```typescript
console.log('Data:', data);
console.error('Error:', error);
```

### API 测试

使用 http://localhost:8000/docs 的 Swagger UI：
1. 点击端点展开
2. 点击 "Try it out"
3. 填写参数
4. 点击 "Execute"

---

## 代码规范

### 后端 (Python)

- 使用类型注解
- Pydantic 模型定义请求/响应
- 异步函数使用 `async def`
- 异常使用 `HTTPException`

```python
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List

class MyRequest(BaseModel):
    field1: str
    field2: Optional[int] = None

@router.post("/")
async def my_endpoint(request: MyRequest):
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid request")
    return {"result": "ok"}
```

### 前端 (TypeScript)

- 使用 TypeScript 类型
- 组件使用函数式组件
- 状态使用 React Hooks
- API 调用封装在 `services/api.ts`

```typescript
import { useState, useEffect } from 'react';
import { myApi } from '../services/api';
import type { MyType } from '../types';

export function MyComponent() {
  const [data, setData] = useState<MyType | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const result = await myApi.getData();
      setData(result);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading ? '加载中...' : data?.content}
    </div>
  );
}
```

---

## 卦象计算逻辑

### 爻的类型

| 数字 | 名称 | 阴阳 | 是否变爻 |
|------|------|------|---------|
| 6 | 老阴 | 阴 | 是（变阳）|
| 7 | 少阳 | 阳 | 否 |
| 8 | 少阴 | 阴 | 否 |
| 9 | 老阳 | 阳 | 是（变阴）|

### 二进制转换

**本卦**:
- 6, 8 → 0（阴爻）
- 7, 9 → 1（阳爻）

**变卦**:
- 6 → 1（老阴变阳）
- 7 → 1（少阳不变）
- 8 → 0（少阴不变）
- 9 → 0（老阳变阴）

### 示例

输入: `[7, 8, 6, 9, 7, 8]`

本卦二进制: `101110` → 翻转 → `011101`
变卦二进制: `101001` → 翻转 → `100101`

变爻位置: 第3爻(6)、第4爻(9)

---

## 常见问题

### Q: 修改后端代码后没有生效？

A: 使用 `--reload` 启动，或手动重启后端服务。

### Q: 前端 API 调用 404？

A: 检查：
1. 后端是否启动
2. 路由是否注册（`router.py`）
3. API 路径是否正确（注意 `/api` 前缀）
4. Vite 代理配置是否正确

### Q: TypeScript 类型错误？

A: 确保前后端类型定义一致：
- 后端：`backend/core/models.py`
- 前端：`frontend/src/types/index.ts`

### Q: Gemini API 报错？

A: 检查：
1. `gemini.json` 中的 API Key 是否正确
2. 网络是否能访问 Google API
3. 模型配额是否用完
4. 后端日志中的详细错误信息

### Q: 卦象数据加载失败？

A: 检查：
1. `data/gua/` 目录是否存在
2. JSON 文件格式是否正确
3. 文件编码是否为 UTF-8

---

## 部署

### 开发环境

```bash
# 后端
cd backend && python main.py

# 前端
cd frontend && npm run dev
```

### 生产环境

```bash
# 后端
cd backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 前端构建
cd frontend && npm run build
# 将 dist/ 目录部署到 Web 服务器
```

---

## 扩展开发建议

### 添加用户历史记录

1. 创建数据库模型存储占卜历史
2. 添加历史记录 API 端点
3. 前端添加历史页面

### 支持多语言

1. 使用 i18n 库（如 react-i18next）
2. 提取所有文本到语言文件
3. 添加语言切换功能

### 添加更多占卜方式

1. 在 `gua_service.py` 实现新的数字生成算法
2. 在 `divination.py` 添加对应 API
3. 前端添加新的交互方式
