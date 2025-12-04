# API 参考文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`

## 占卜接口

### 计算卦象

根据六个数字计算本卦和变卦。

**请求**

```
POST /api/divination/calculate
```

```json
{
  "numbers": [7, 8, 9, 6, 7, 8],
  "question": "我的事业发展如何？"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| numbers | number[] | 是 | 6个数字，范围 6-9 |
| question | string | 是 | 占卜问题 |

**响应**

```json
{
  "numbers": [7, 8, 9, 6, 7, 8],
  "ben_gua": {
    "index": 11,
    "name": "泰",
    "symbol": "䷊",
    "description": "地天泰",
    "judgement": "小往大来，吉，亨"
  },
  "bian_gua": {
    "index": 19,
    "name": "临",
    "symbol": "䷒",
    "description": "地泽临",
    "judgement": "元亨利贞"
  },
  "changing_lines": [
    {
      "position": 3,
      "yaoci": "九三：无平不陂，无往不复"
    },
    {
      "position": 4,
      "yaoci": "六四：翩翩不富，以其邻"
    }
  ]
}
```

### 随机占卜

模拟三枚硬币投掷，生成随机卦象。

**请求**

```
POST /api/divination/random
```

```json
{
  "question": "最近的感情运势如何？"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 占卜问题 |

**响应**

与计算卦象接口相同。

### 获取卦象信息

根据卦序号获取完整卦象数据。

**请求**

```
GET /api/divination/gua/{index}
```

| 参数 | 类型 | 说明 |
|------|------|------|
| index | number | 卦序号 (1-64) |

**响应**

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
    },
    {
      "position": 2,
      "yaoci": "九二：见龙在田，利见大人"
    }
  ]
}
```

## AI 解卦接口

### 分析卦象

调用 Gemini AI 对卦象进行解读。

**请求**

```
POST /api/interpretation/analyze
```

```json
{
  "question": "我的事业发展如何？",
  "ben_gua": {
    "index": 11,
    "name": "泰",
    "symbol": "䷊",
    "description": "地天泰"
  },
  "bian_gua": {
    "index": 19,
    "name": "临",
    "symbol": "䷒",
    "description": "地泽临"
  },
  "changing_lines": [
    {
      "position": 3,
      "yaoci": "九三：无平不陂，无往不复"
    }
  ]
}
```

**响应**

```json
{
  "summary": "泰卦主通达顺利，变临卦示机遇将至...",
  "interpretation": "此卦显示您的事业正处于上升期..."
}
```

## 错误响应

所有接口在出错时返回统一格式：

```json
{
  "detail": "错误描述信息"
}
```

常见状态码：

| 状态码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 数据模型

### GuaInfo

卦象基本信息。

```typescript
interface GuaInfo {
  index: number;      // 卦序号 (1-64)
  name: string;       // 卦名
  symbol?: string;    // Unicode 卦符
  description: string; // 卦象描述
  judgement?: string; // 卦辞
  image?: string;     // 象辞
  lines?: Line[];     // 爻辞
}
```

### ChangingLine

变爻信息。

```typescript
interface ChangingLine {
  position: number;  // 爻位 (1-6)
  yaoci: string;     // 爻辞
}
```

### DivinationResponse

占卜响应。

```typescript
interface DivinationResponse {
  numbers?: number[];        // 占卜数字
  ben_gua: GuaInfo;          // 本卦
  bian_gua: GuaInfo;         // 变卦
  changing_lines: ChangingLine[]; // 变爻列表
}
```

### InterpretationResponse

AI 解读响应。

```typescript
interface InterpretationResponse {
  summary: string;        // 简要总结
  interpretation: string; // 详细解读
}
```
