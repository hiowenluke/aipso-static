#!/bin/bash

# 重命名 headshot-ai 为 business-headshot-ai
# 包括文件夹和所有相关代码引用

set -e

echo "============================================================"
echo "🔄 重命名 headshot-ai 为 business-headshot-ai"
echo "============================================================"
echo ""

# 1. 重命名文件夹
echo "📁 步骤 1: 重命名文件夹..."
if [ -d "static/headshot-ai" ]; then
    mv static/headshot-ai static/business-headshot-ai
    echo "✅ static/headshot-ai -> static/business-headshot-ai"
else
    echo "⚠️  static/headshot-ai 不存在，跳过"
fi

if [ -d "tools/filelist-generator/headshot-ai" ]; then
    mv tools/filelist-generator/headshot-ai tools/filelist-generator/business-headshot-ai
    echo "✅ tools/filelist-generator/headshot-ai -> tools/filelist-generator/business-headshot-ai"
else
    echo "⚠️  tools/filelist-generator/headshot-ai 不存在，跳过"
fi

echo ""

# 2. 替换文件内容中的 headshot-ai
echo "📝 步骤 2: 替换文件内容中的 'headshot-ai' 为 'business-headshot-ai'..."

# 使用 find 和 sed 替换（macOS 兼容）
find . -type f \( \
    -name "*.md" -o \
    -name "*.py" -o \
    -name "*.sh" -o \
    -name "*.html" -o \
    -name "*.txt" -o \
    -name ".gitignore" \
\) ! -path "./.git/*" ! -path "./tools/rename-headshot-to-business.sh" \
    -exec sed -i '' 's/headshot-ai/business-headshot-ai/g' {} \;

echo "✅ 已替换所有文件中的 'headshot-ai'"
echo ""

# 3. 替换 HEADSHOT AI 为 BUSINESS HEADSHOT AI
echo "📝 步骤 3: 替换 'HEADSHOT AI' 为 'BUSINESS HEADSHOT AI'..."

find . -type f \( \
    -name "*.html" -o \
    -name "*.md" \
\) ! -path "./.git/*" \
    -exec sed -i '' 's/HEADSHOT AI/BUSINESS HEADSHOT AI/g' {} \;

echo "✅ 已替换所有文件中的 'HEADSHOT AI'"
echo ""

# 4. 替换 Headshot AI 为 Business Headshot AI
echo "📝 步骤 4: 替换 'Headshot AI' 为 'Business Headshot AI'..."

find . -type f \( \
    -name "*.html" -o \
    -name "*.md" \
\) ! -path "./.git/*" \
    -exec sed -i '' 's/Headshot AI/Business Headshot AI/g' {} \;

echo "✅ 已替换所有文件中的 'Headshot AI'"
echo ""

echo "============================================================"
echo "✅ 重命名完成！"
echo "============================================================"
echo ""
echo "📋 已完成的操作："
echo "  1. ✅ 重命名文件夹"
echo "  2. ✅ 替换代码中的 'headshot-ai' -> 'business-headshot-ai'"
echo "  3. ✅ 替换文本中的 'HEADSHOT AI' -> 'BUSINESS HEADSHOT AI'"
echo "  4. ✅ 替换文本中的 'Headshot AI' -> 'Business Headshot AI'"
echo ""
echo "💡 下一步："
echo "  1. 检查修改: git status"
echo "  2. 查看差异: git diff"
echo "  3. 重新生成文件列表: ./generate-filelist.sh business-headshot-ai"
echo "  4. 提交更改: git add . && git commit -m 'Rename headshot-ai to business-headshot-ai'"
echo ""
