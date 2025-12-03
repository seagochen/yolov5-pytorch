#!/bin/bash

# IChing AI 解卦系统 - 开发环境启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   IChing AI 解卦系统 - 开发环境${NC}"
echo -e "${GREEN}========================================${NC}"
echo

# 检查 gemini.json 是否存在
if [ ! -f "gemini.json" ]; then
    echo -e "${RED}错误: gemini.json 文件不存在${NC}"
    echo -e "${YELLOW}请复制 gemini.json.example 为 gemini.json 并填入您的 API Key${NC}"
    echo "  cp gemini.json.example gemini.json"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到 python3${NC}"
    exit 1
fi

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到 node${NC}"
    exit 1
fi

# 检查 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到 npm${NC}"
    exit 1
fi

echo -e "${GREEN}环境检查通过${NC}"
echo

# 安装后端依赖
echo -e "${YELLOW}正在检查后端依赖...${NC}"
cd backend
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}后端依赖安装完成${NC}"
cd ..

# 安装前端依赖
echo -e "${YELLOW}正在检查前端依赖...${NC}"
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi
echo -e "${GREEN}前端依赖安装完成${NC}"
cd ..

echo
echo -e "${GREEN}启动服务...${NC}"
echo

# 启动后端
echo -e "${YELLOW}启动后端服务 (http://localhost:8000)...${NC}"
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 2

# 启动前端
echo -e "${YELLOW}启动前端服务 (http://localhost:3000)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}服务已启动!${NC}"
echo -e "${GREEN}前端: http://localhost:3000${NC}"
echo -e "${GREEN}后端: http://localhost:8000${NC}"
echo -e "${GREEN}API 文档: http://localhost:8000/docs${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "${YELLOW}按 Ctrl+C 停止所有服务${NC}"

# 等待用户中断
cleanup() {
    echo
    echo -e "${YELLOW}正在停止服务...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}服务已停止${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 保持脚本运行
wait
