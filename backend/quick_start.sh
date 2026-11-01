#!/bin/bash
# 快速启动后端服务

echo "=========================================="
echo "正在启动后端服务..."
echo "=========================================="

# 进入脚本所在目录
cd "$(dirname "$0")"

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  8000端口已被占用，正在停止..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# 检查依赖
echo "检查依赖..."
python3 -c "import dotenv, requests, fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "安装依赖..."
    pip3 install python-dotenv requests fastapi uvicorn sqlalchemy pymysql
fi

# 启动服务
echo ""
echo "🚀 启动服务中..."
echo "=========================================="
python3 start.py
