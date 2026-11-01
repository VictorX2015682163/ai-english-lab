#!/bin/bash
# 后端服务启动脚本

# 进入后端目录
cd "$(dirname "$0")"

# 停止已运行的服务
echo "正在停止旧服务..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

# 检查端口是否被占用
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  警告: 8000端口仍被占用，尝试强制停止..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# 清理Python缓存
echo "清理缓存..."
find . -name "*.pyc" -delete 2>/dev/null
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null

# 启动服务
echo "正在启动后端服务..."
echo "================================"
python3 main.py

