#!/usr/bin/env python3
"""
测试文件监视功能
"""

import sys
from pathlib import Path

# 测试路径
STORE_DIR = Path(__file__).parent.parent.parent / 'static'
FILELIST_GENERATOR = Path(__file__).parent.parent / 'filelist-generator' / 'generate-filelist.py'
SERVER_STORE_DIR = Path('/Users/luyunfei/Desktop/________/____AI 摄影/____aipso-app/aipso-server/static')

print("=" * 60)
print("🧪 测试文件监视配置")
print("=" * 60)
print()

# 检查路径
checks = [
    ("Store 目录", STORE_DIR),
    ("生成器脚本", FILELIST_GENERATOR),
    ("Server static 目录", SERVER_STORE_DIR),
]

all_ok = True
for name, path in checks:
    exists = path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {name}: {path}")
    if not exists:
        all_ok = False

print()
if all_ok:
    print("✅ 所有路径检查通过")
    print()
    print("可以运行:")
    print("  ./start-watch.sh")
else:
    print("❌ 部分路径不存在，请检查配置")
    print()
    print("需要修改 watch-and-sync.py 中的 SERVER_STORE_DIR 配置")

print()
print("=" * 60)
