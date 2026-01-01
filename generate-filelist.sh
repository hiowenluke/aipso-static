#!/bin/bash

# 生成文件列表
# 用法:
#   ./generate-filelist.sh <product_slug>  # 生成指定产品
#   ./generate-filelist.sh all             # 生成所有产品

# 检查是否提供了参数
if [ $# -eq 0 ]; then
    echo "❌ 错误: 缺少参数"
    echo ""
    echo "用法:"
    echo "  $0 <product_slug>    生成指定产品的文件列表"
    echo "  $0 all               生成所有产品的文件列表"
    echo ""
    echo "示例:"
    echo "  $0 business-headshot-ai       只生成 business-headshot-ai 的文件列表"
    echo "  $0 all               生成所有产品的文件列表"
    echo ""
    echo "可用的产品:"
    ls -d static/*/ 2>/dev/null | sed 's|static/||g' | sed 's|/||g' | sed 's/^/  • /'
    exit 1
fi

# 获取命令行参数
PRODUCT_ARG="$1"

# 显示帮助信息
if [ "$PRODUCT_ARG" = "-h" ] || [ "$PRODUCT_ARG" = "--help" ]; then
    echo "用法:"
    echo "  $0 <product_slug>    生成指定产品的文件列表"
    echo "  $0 all               生成所有产品的文件列表"
    echo ""
    echo "示例:"
    echo "  $0 business-headshot-ai       只生成 business-headshot-ai 的文件列表"
    echo "  $0 all               生成所有产品的文件列表"
    echo ""
    echo "可用的产品:"
    ls -d static/*/ 2>/dev/null | sed 's|static/||g' | sed 's|/||g' | sed 's/^/  • /'
    exit 0
fi

# 如果参数为 "all"，生成所有产品
if [ "$PRODUCT_ARG" = "all" ]; then
    echo "🚀 开始生成所有产品的文件列表..."
    echo ""
    
    python3 tools/filelist-generator/generate-filelist.py
    
    echo ""
    echo "✅ 完成！"
    echo ""
    echo "📂 生成的文件列表位于 tools/filelist-generator/ 目录下"
    echo ""
    echo "💡 提示："
    echo "   • 查看文件列表: cat tools/filelist-generator/business-headshot-ai/files.txt"
    echo "   • 测试解析器: python3 tools/filelist-generator/filelist_parser.py"
    echo ""
else
    # 生成指定产品
    echo "🚀 开始生成 $PRODUCT_ARG 的文件列表..."
    echo ""
    
    # 检查产品目录是否存在
    if [ ! -d "static/$PRODUCT_ARG" ]; then
        echo "❌ 错误: 产品目录 'static/$PRODUCT_ARG' 不存在"
        echo ""
        echo "可用的产品:"
        ls -d static/*/ 2>/dev/null | sed 's|static/||g' | sed 's|/||g' | sed 's/^/  • /'
        exit 1
    fi
    
    python3 tools/filelist-generator/generate-filelist.py "$PRODUCT_ARG"
    
    echo ""
    echo "✅ 完成！"
    echo ""
    echo "📂 生成的文件列表: tools/filelist-generator/$PRODUCT_ARG/files.txt"
    echo ""
    echo "💡 提示："
    echo "   • 查看文件列表: cat tools/filelist-generator/$PRODUCT_ARG/files.txt"
    echo "   • 查看文件数量: wc -l tools/filelist-generator/$PRODUCT_ARG/files.txt"
    echo "   • 测试解析器: python3 tools/filelist-generator/filelist_parser.py"
    echo ""
fi
