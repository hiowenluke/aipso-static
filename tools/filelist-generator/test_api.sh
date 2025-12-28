#!/bin/bash

# API 测试脚本
# 用法: ./test_api.sh [base_url]

BASE_URL="${1:-http://localhost:5000}"

echo "=========================================="
echo "API 测试脚本"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    
    echo -e "${BLUE}测试: $name${NC}"
    echo "GET $endpoint"
    echo ""
    
    curl -s "$BASE_URL$endpoint" | python3 -m json.tool | head -30
    
    echo ""
    echo "----------------------------------------"
    echo ""
}

# 1. 健康检查
test_endpoint "健康检查" "/api/health"

# 2. 获取文件列表（第1页）
test_endpoint "文件列表（第1页）" "/api/files?page=1&page_size=5"

# 3. 获取所有分类
test_endpoint "所有分类" "/api/categories"

# 4. 获取 home 分类
test_endpoint "Home 分类" "/api/categories/home?page=1&page_size=5"

# 5. 搜索文件
test_endpoint "搜索 'blur'" "/api/search?q=blur"

# 6. 获取目录结构
test_endpoint "目录结构 (images/)" "/api/directory?path=images/"

# 7. 获取统计信息
test_endpoint "统计信息" "/api/stats"

echo -e "${GREEN}✅ 测试完成！${NC}"
echo ""
echo "更多测试："
echo "  curl $BASE_URL/api/files?page=2&page_size=10"
echo "  curl $BASE_URL/api/categories/backdrops"
echo "  curl $BASE_URL/api/search?q=City&case_sensitive=true"
echo ""
