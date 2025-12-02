# 快速上手

5 分钟启动 IChing AI 解卦系统，开始你的智能占卜之旅。

---

## 环境要求

- **Python**: 3.8+
- **Node.js**: 16+
- **Google Gemini API Key**: [获取地址](https://aistudio.google.com/apikey)

## 安装步骤

### 1. 配置 API Key

在项目根目录创建 `gemini.json`：

```json
{
  "api_key": "你的-Gemini-API-Key"
}
```

### 2. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend && npm install && cd ..
```

### 3. 启动服务

**终端 1 - 后端**

```bash
cd backend
python main.py
```

**终端 2 - 前端**

```bash
cd frontend
npm run dev
```

### 4. 访问应用

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 | http://localhost:8000/docs |

---

## 使用流程

### 第一步：输入问题

在页面顶部的输入框中输入你想要占卜的问题，例如：
- "这份工作适合我吗？"
- "近期投资运势如何？"
- "感情方面有什么建议？"

### 第二步：起卦

有两种起卦方式：

**方式一：随机摇卦（推荐）**

点击"摇卦"按钮，系统会模拟三枚硬币投掷6次，自动生成卦象。

**方式二：手动输入**

输入6个数字（6-9），每个数字代表一爻：
- **6**: 老阴（变爻，阴变阳）
- **7**: 少阳（不变阳爻）
- **8**: 少阴（不变阴爻）
- **9**: 老阳（变爻，阳变阴）

### 第三步：查看卦象

系统会显示：
- **本卦**: 当前状态的卦象
- **变卦**: 发展趋势的卦象
- **变爻**: 需要特别关注的爻位及爻辞

### 第四步：AI 解卦

点击"AI 解卦"按钮，Gemini AI 会根据你的问题和卦象给出详细解读，包括：
- 卦象概述
- 针对问题的解读
- 变爻分析
- 变卦趋势
- 综合建议

---

## 64卦数据

系统内置完整的周易64卦数据，包括：
- 卦名和别名
- 卦辞
- 六爻爻辞
- 卦象图案

数据存储在 `data/gua/` 目录下的 JSON 文件中。

---

## 常见问题

### 后端启动失败

```bash
# 检查 Python 版本
python --version  # 需要 3.8+

# 安装缺失的依赖
pip install fastapi uvicorn google-generativeai pydantic
```

### 前端连接失败

确保后端已启动（端口 8000），检查浏览器控制台错误信息。

前端默认代理配置会将 `/api` 请求转发到 `http://localhost:8000`。

### API 调用报错

1. 检查 `gemini.json` 中的 API Key 是否正确
2. 检查网络是否能访问 Google API
3. 查看后端终端日志了解详细错误

### 卦象数据加载失败

确保 `data/gua/` 目录存在且包含正确格式的 JSON 文件。

---

## 下一步

- [技术架构](02-ARCHITECTURE.md) - 了解系统设计
- [API 参考](03-API-REFERENCE.md) - 开发接口文档
- [开发指南](04-DEVELOPMENT.md) - 参与代码开发
