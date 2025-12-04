# 快速部署指南

## 环境要求

### 后端环境
- Python 3.10+
- pip 包管理器

### 前端环境
- Node.js 18+
- npm 或 yarn

### API 配置
- Google Gemini API Key

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd IChing
```

### 2. 配置 Gemini API Key

在项目根目录创建 `gemini.json` 文件：

```json
{
  "api_key": "YOUR_GEMINI_API_KEY"
}
```

> 获取 API Key: https://makersuite.google.com/app/apikey

### 3. 启动后端服务

```bash
cd backend

# 安装依赖
pip install -r ../requirements.txt

# 启动服务 (默认端口 8000)
python main.py
```

后端启动后访问 http://localhost:8000/docs 查看 API 文档。

### 4. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (端口 3000)
npm run dev
```

前端启动后访问 http://localhost:3000 开始使用。

## 生产环境部署

### 后端部署

使用 uvicorn 生产配置：

```bash
pip install uvicorn[standard]
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 前端构建

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/` 目录，可部署到任意静态服务器。

### 环境变量

前端可通过环境变量配置 API 地址：

```bash
VITE_API_URL=https://your-api-domain.com npm run build
```

## 常见问题

### CORS 错误

后端已配置允许所有来源的 CORS 请求。如需限制，修改 `backend/main.py` 中的 CORS 配置。

### API Key 无效

确保 `gemini.json` 文件格式正确，API Key 有效且有 Gemini API 访问权限。

### 端口冲突

- 后端默认端口: 8000
- 前端默认端口: 3000

如需修改，分别修改 `backend/main.py` 和 `frontend/vite.config.ts`。
