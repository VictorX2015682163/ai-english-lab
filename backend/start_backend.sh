#!/bin/bash
# 启动后端服务脚本

cd "$(dirname "$0")"

# 清理端口
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 1

# 使用正确的Python路径启动
/usr/bin/python3 start.py
