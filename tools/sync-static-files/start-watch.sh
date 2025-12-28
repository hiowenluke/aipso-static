#!/bin/bash

# 启动文件监视和同步工具

echo "🚀 启动文件监视和同步工具..."
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

# 检查 watchdog 是否安装
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo "❌ 错误: 缺少依赖 watchdog"
    echo ""
    echo "请安装依赖:"
    echo "  pip3 install watchdog"
    echo ""
    exit 1
fi

# 启动监视
python3 tools/sync-static-files/watch-and-sync.py
