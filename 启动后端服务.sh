#!/bin/bash
# 快速启动后端服务脚本

cd "$(dirname "$0")/backend"

echo "=========================================="
echo "正在启动后端服务..."
echo "=========================================="

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  8000端口已被占用，正在停止..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

# 启动服务
echo "🚀 启动服务中..."
python3 start.py
