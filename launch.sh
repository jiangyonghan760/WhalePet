#!/bin/sh
# macOS / Linux 启动脚本
cd "$(dirname "$0")" || exit 1
exec python3 run.py
