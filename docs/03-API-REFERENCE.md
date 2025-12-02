# API 参考手册

所有 API 的完整参考文档。

- **Base URL**: `http://localhost:8000/api`
- **数据格式**: JSON
- **在线文档**: http://localhost:8000/docs（启动后端后可用）

---

## 占卜 API

### 计算卦象

根据输入的6个数字（6-9）计算卦象。

```http
POST /api/divination/calculate
```

**请求**:
```json
{
  "numbers": [7, 8, 6, 9, 7, 8],
  "question": "这份工作适合我吗？"
}
```

**参数说明**:
- `numbers` (必填): 6个数字的数组，每个数字必须是 6、7、8、9 之一
  - **6**: 老阴（变爻）
  - **7**: 少阳（不变）
  - **8**: 少阴（不变）
  - **9**: 老阳（变爻）
- `question` (可选): 占卜的问题

**响应**:
```json
{
  "ben_gua": {
    "name": "既济",
    "binary": "101010",
    "description": "亨小，利贞...",
    "image": "———————\n——   ——\n———————\n——   ——\n———————\n——   ——",
    "yaoci": ["初九：...", "六二：...", ...]
  },
  "bian_gua": {
    "name": "未济",
    "binary": "010101",
    "description": "亨，小狐汔济...",
    "image": "——   ——\n———————\n——   ——\n———————\n——   ——\n———————",
    "yaoci": ["初六：...", "九二：...", ...]
  },
  "changing_lines": [
    {
      "position": 3,
      "yaoci": "六三：高宗伐鬼方..."
    },
    {
      "position": 4,
      "yaoci": "九四：繻有衣袽..."
    }
  ],
  "question": "这份工作适合我吗？",
  "numbers": [7, 8, 6, 9, 7, 8]
}
```

---

### 随机摇卦

模拟三枚硬币投掷，随机生成卦象。

```http
POST /api/divination/random
```

**请求**:
```json
{
  "question": "近期运势如何？"
}
```

**参数说明**:
- `question` (可选): 占卜的问题

**响应**: 与 `/calculate` 相同

**概率分布**:
模拟三枚硬币投掷，概率如下：
- 6 (老阴): 1/8 = 12.5%
- 7 (少阳): 3/8 = 37.5%
- 8 (少阴): 3/8 = 37.5%
- 9 (老阳): 1/8 = 12.5%

---

### 获取64卦列表

获取所有64卦的基本信息。

```http
GET /api/divination/gua
```

**响应**:
```json
[
  {
    "binary": "000000",
    "name": "坤",
    "alternate_name": "坤为地",
    "description": "元亨，利牝马之贞..."
  },
  {
    "binary": "000001",
    "name": "剥",
    "alternate_name": "山地剥",
    "description": "不利有攸往..."
  },
  ...
]
```

---

### 查询单个卦象

根据二进制编码获取卦象详情。

```http
GET /api/divination/gua/{binary}
```

**参数**:
- `binary`: 6位二进制字符串（如 "111111"）

**示例**:
```http
GET /api/divination/gua/111111
```

**响应**:
```json
{
  "binary": "111111",
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
  ],
  "image": "———————\n———————\n———————\n———————\n———————\n———————"
}
```

**错误响应**:
```json
{
  "detail": "二进制编码必须是6位0/1字符串"
}
```

---

## 解卦 API

### AI 解读卦象

使用 Gemini AI 对卦象进行智能解读。

```http
POST /api/interpretation/analyze
```

**请求**:
```json
{
  "question": "这份工作适合我吗？",
  "ben_gua": {
    "name": "既济",
    "description": "亨小，利贞...",
    "image": "———————\n——   ——\n..."
  },
  "bian_gua": {
    "name": "未济",
    "description": "亨，小狐汔济...",
    "image": "——   ——\n———————\n..."
  },
  "changing_lines": [
    {
      "position": 3,
      "yaoci": "六三：高宗伐鬼方..."
    }
  ]
}
```

**参数说明**:
- `question` (必填): 占卜的问题
- `ben_gua` (必填): 本卦信息
- `bian_gua` (必填): 变卦信息
- `changing_lines` (必填): 变爻列表

**响应**:
```json
{
  "interpretation": "【卦象概述】\n既济卦象征事情已经成功...\n\n【针对问题的解读】\n...\n\n【变爻分析】\n...\n\n【变卦趋势】\n...\n\n【综合建议】\n...",
  "summary": "这份工作适合你，但需要注意保持警惕，防止成功后的懈怠。"
}
```

**解读结构**:
AI 解读包含以下部分：
1. **卦象概述**: 本卦的基本含义
2. **针对问题的解读**: 结合用户问题的分析
3. **变爻分析**: 变爻的特殊意义
4. **变卦趋势**: 发展趋势预测
5. **综合建议**: 实际可行的建议

---

## 通用端点

### 根路径

```http
GET /
```

**响应**:
```json
{
  "message": "IChing AI 解卦系统",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "healthy"
}
```

---

## 错误响应

所有 API 在出错时返回统一格式：

```json
{
  "detail": "错误信息"
}
```

**常见状态码**:
- `400`: 请求参数错误
  - 数字不在 6-9 范围内
  - 二进制编码格式错误
  - 问题为空
- `404`: 资源不存在（如卦象不存在）
- `500`: 服务器内部错误
  - Gemini API 调用失败
  - 卦象数据加载失败

---

## 数据类型定义

### TypeScript 类型

完整的 TypeScript 类型定义见 `frontend/src/types/index.ts`：

```typescript
interface GuaInfo {
  name: string;
  binary: string;
  description: string;
  image: string;
  yaoci?: string[];
}

interface ChangingLine {
  position: number;
  yaoci: string;
}

interface DivinationResult {
  ben_gua: GuaInfo;
  bian_gua: GuaInfo;
  changing_lines: ChangingLine[];
  question?: string;
  numbers?: number[];
}

interface InterpretationResult {
  interpretation: string;
  summary: string;
}
```

### Python 模型

完整的 Pydantic 模型定义见 `backend/core/models.py`。

---

## 使用示例

### cURL 示例

**随机摇卦**:
```bash
curl -X POST http://localhost:8000/api/divination/random \
  -H "Content-Type: application/json" \
  -d '{"question": "今天运势如何？"}'
```

**计算卦象**:
```bash
curl -X POST http://localhost:8000/api/divination/calculate \
  -H "Content-Type: application/json" \
  -d '{"numbers": [7, 8, 6, 9, 7, 8], "question": "工作运势"}'
```

**AI 解卦**:
```bash
curl -X POST http://localhost:8000/api/interpretation/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "工作运势",
    "ben_gua": {"name": "乾", "description": "元亨利贞", "image": "..."},
    "bian_gua": {"name": "坤", "description": "元亨利牝马之贞", "image": "..."},
    "changing_lines": []
  }'
```

### JavaScript 示例

```javascript
// 使用 fetch
const result = await fetch('/api/divination/random', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: '今天运势如何？' })
}).then(res => res.json());

console.log(result.ben_gua.name); // 输出本卦名称
```
