"""
Server 端 API 集成示例
展示如何使用 FileListParser 构建 RESTful API
"""

from flask import Flask, jsonify, request, send_file
from pathlib import Path
from filelist_parser import FileListParser
import os

app = Flask(__name__)

# 配置
STORE_ROOT = Path(__file__).parent.parent.parent / 'static'
PRODUCT_SLUG = 'business-headshot-ai'
FILELIST_PATH = Path(__file__).parent / PRODUCT_SLUG / 'files.txt'

# 初始化解析器
try:
    parser = FileListParser(str(FILELIST_PATH))
    print(f"✅ 文件列表加载成功: {parser.get_total_count()} 个文件")
except FileNotFoundError:
    print(f"❌ 文件列表不存在: {FILELIST_PATH}")
    print("请先运行: ./generate-filelist.sh business-headshot-ai")
    parser = None


# ==================== API 端点 ====================

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'product': PRODUCT_SLUG,
        'total_files': parser.get_total_count() if parser else 0
    })


@app.route('/api/files')
def get_files():
    """
    获取文件列表（分页）
    
    Query Parameters:
        page: 页码（默认 1）
        page_size: 每页数量（默认 20，最大 100）
    
    Example:
        GET /api/files?page=1&page_size=20
    """
    if not parser:
        return jsonify({'error': 'File list not loaded'}), 500
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    # 限制 page_size
    page_size = min(page_size, 100)
    
    data = parser.get_page(page, page_size)
    
    # 添加完整 URL
    base_url = request.host_url.rstrip('/')
    data['items'] = [
        {
            'path': item,
            'url': f"{base_url}/{PRODUCT_SLUG}/{item}"
        }
        for item in data['items']
    ]
    
    return jsonify(data)


@app.route('/api/categories')
def get_categories():
    """
    获取所有分类
    
    Example:
        GET /api/categories
    """
    if not parser:
        return jsonify({'error': 'File list not loaded'}), 500
    
    categories = {
        'home': '首页图片',
        'faces': '人脸图片',
        'backdrops': '背景图片',
        'poses': '姿势图片',
        'outfits': '服装图片',
        'hairstyles': '发型图片',
        'expressions': '表情图片',
        'glasses': '眼镜图片',
    }
    
    result = []
    for key, name in categories.items():
        files = parser.get_files_by_category(key)
        if files:
            result.append({
                'key': key,
                'name': name,
                'count': len(files)
            })
    
    return jsonify({
        'total': len(result),
        'categories': result
    })


@app.route('/api/categories/<category>')
def get_category_files(category):
    """
    获取分类文件（分页）
    
    Path Parameters:
        category: 分类名称（home, faces, backdrops, etc.）
    
    Query Parameters:
        page: 页码（默认 1）
        page_size: 每页数量（默认 20，最大 100）
    
    Example:
        GET /api/categories/home?page=1&page_size=20
    """
    if not parser:
        return jsonify({'error': 'File list not loaded'}), 500
    
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    # 限制 page_size
    page_size = min(page_size, 100)
    
    data = parser.get_paginated_category(category, page, page_size)
    
    # 添加完整 URL
    base_url = request.host_url.rstrip('/')
    data['items'] = [
        {
            'path': item,
            'url': f"{base_url}/{PRODUCT_SLUG}/{item}"
        }
        for item in data['items']
    ]
    
    return jsonify(data)


@app.route('/api/search')
def search_files():
    """
    搜索文件
    
    Query Parameters:
        q: 搜索关键词（必需）
        case_sensitive: 是否区分大小写（默认 false）
    
    Example:
        GET /api/search?q=blur
        GET /api/search?q=City&case_sensitive=true
    """
    if not parser:
        return jsonify({'error': 'File list not loaded'}), 500
    
    keyword = request.args.get('q', '').strip()
    if not keyword:
        return jsonify({'error': 'Missing keyword'}), 400
    
    case_sensitive = request.args.get('case_sensitive', 'false').lower() == 'true'
    
    files = parser.search(keyword, case_sensitive)
    
    # 添加完整 URL
    base_url = request.host_url.rstrip('/')
    items = [
        {
            'path': item,
            'url': f"{base_url}/{PRODUCT_SLUG}/{item}"
        }
        for item in files
    ]
    
    return jsonify({
        'keyword': keyword,
        'case_sensitive': case_sensitive,
        'total': len(items),
        'items': items
    })


@app.route('/api/directory')
def get_directory():
    """
    获取目录结构
    
    Query Parameters:
        path: 目录路径（默认为根目录）
    
    Example:
        GET /api/directory?path=images/
        GET /api/directory?path=images/home/
    """
    if not parser:
        return jsonify({'error': 'File list not loaded'}), 500
    
    path = request.args.get('path', '').strip()
    
    structure = parser.get_directory_structure(path)
    
    return jsonify({
        'path': path or '/',
        'directories': structure['directories'],
        'files': structure['files'],
        'total_directories': len(structure['directories']),
        'total_files': len(structure['files'])
    })


@app.route('/api/stats')
def get_stats():
    """
    获取统计信息
    
    Example:
        GET /api/stats
    """
    if not parser:
        return jsonify({'error': 'File list not loaded'}), 500
    
    # 统计各分类的文件数
    categories = ['home', 'faces', 'backdrops', 'poses', 'outfits', 'hairstyles']
    category_stats = {}
    
    for category in categories:
        files = parser.get_files_by_category(category)
        category_stats[category] = len(files)
    
    # 统计文件格式
    all_files = parser.get_all_files()
    format_stats = {}
    for file_path in all_files:
        ext = Path(file_path).suffix.lower()
        format_stats[ext] = format_stats.get(ext, 0) + 1
    
    return jsonify({
        'total_files': parser.get_total_count(),
        'categories': category_stats,
        'formats': format_stats
    })


# ==================== 静态文件服务 ====================

@app.route('/<product>/<path:file_path>')
def serve_file(product, file_path):
    """
    提供静态文件服务
    
    Example:
        GET /business-headshot-ai/images/home/City/city-1.webp
    """
    if product != PRODUCT_SLUG:
        return jsonify({'error': 'Product not found'}), 404
    
    full_path = STORE_ROOT / product / file_path
    
    if not full_path.exists() or not full_path.is_file():
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(full_path)


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== 主函数 ====================

def main():
    """启动服务器"""
    print("=" * 60)
    print("🚀 Static Resource API Server")
    print("=" * 60)
    print(f"Product: {PRODUCT_SLUG}")
    print(f"Store Root: {STORE_ROOT}")
    print(f"Total Files: {parser.get_total_count() if parser else 0}")
    print()
    print("API Endpoints:")
    print("  GET  /api/health              - 健康检查")
    print("  GET  /api/files               - 获取文件列表（分页）")
    print("  GET  /api/categories          - 获取所有分类")
    print("  GET  /api/categories/<name>   - 获取分类文件（分页）")
    print("  GET  /api/search?q=<keyword>  - 搜索文件")
    print("  GET  /api/directory?path=<p>  - 获取目录结构")
    print("  GET  /api/stats               - 获取统计信息")
    print()
    print("Static Files:")
    print(f"  GET  /{PRODUCT_SLUG}/<path>   - 访问静态文件")
    print()
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    main()
