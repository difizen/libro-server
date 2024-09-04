#!/bin/bash

# 检查 PORT 环境变量是否设置
if [ -z "$PORT" ]; then
  echo "PORT 环境变量未设置"
  exit 1
fi

# 启动 libro，并将 PORT 环境变量传递给它
exec libro --port="$PORT" --notebook-dir="/home/admin/workspace"
