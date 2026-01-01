# 文件列表工具使用指南

## 概述

这套工具用于生成和解析静态资源文件列表，专为 S3/CloudFront 模拟环境设计。

## 设计理念

### 为什么只存储文件名？

1. **精简高效**：只存储必要信息，文件体积小，加载快
2. **灵活性**：文件大小、修改时间等元数据由 server 端动态获取
3. **易维护**：文件列表简单，易于版本控制和对比
4. **快速解析**：纯文本格式，解析速度极快

### 数据格式

```
images/home/City/city-1.webp
images/home/City/city-2.webp
images/home/Studio/Light/studio-1.webp
images/options/backdrops/1@Studio/Dark-Gradients/blur-0.webp
```

- 每行一个文件路径
- 使用 POSIX 路径格式（`/` 分隔符）
- 按字典序排序（便于二分查找）
- UTF-8 编码

## 工具说明

### 1. 生成工具 (generate-filelist.py)

生成产品的文件列表。

#### 使用方法

```bash
# 生成所有产品的文件列表
python3 tools/generate-filelist.py

# 生成指定产品的文件列表
python3 tools/generate-filelist.py business-headshot-ai

# 生成 JSON 格式
python3 tools/generate-filelist.py business-headshot-ai json
```

#### 输出位置

```
tools/filelist-generator/business-headshot-ai/files.txt
```

#### 特性

- ✅ 自动扫描所有图片文件（.webp, .jpg, .jpeg, .png, .gif）
- ✅ 跳过隐藏文件和目录
- ✅ 按字典序排序
- ✅ 支持 TXT 和 JSON 格式

### 2. 解析库 (filelist_parser.py)

供 server 端使用的 Python 解析库。

#### 快速开始

```python
from tools.filelist_parser import FileListParser

# 初始化解析器
parser = FileListParser('tools/filelist-generator/business-headshot-ai/files.txt')

# 获取总数
total = parser.get_total_count()
print(f"总文件数: {total}")

# 获取分页数据
page_data = parser.get_page(page=1, page_size=20)
print(f"第 1 页: {len(page_data['items'])} 个文件")
```

#### API 文档

##### 基础方法

**get_all_files()**
```python
files = parser.get_all_files()
# 返回: ['images/home/city-1.webp', ...]
```

**get_total_count()**
```python
total = parser.get_total_count()
# 返回: 998
```

**get_page(page, page_size)**
```python
page_data = parser.get_page(page=1, page_size=20)
# 返回:
# {
#     'page': 1,
#     'page_size': 20,
#     'total': 998,
#     'total_pages': 50,
#     'items': ['images/home/city-1.webp', ...]
# }
```

##### 过滤方法

**filter_by_prefix(prefix)**
```python
# 获取 images/home/ 目录下的所有文件（包含子目录）
files = parser.filter_by_prefix('images/home/')
# 返回: ['images/home/City/city-1.webp', 'images/home/Studio/studio-1.webp', ...]
```

**filter_by_directory(directory)**
```python
# 获取 images/home/City 目录下的文件（不包含子目录）
files = parser.filter_by_directory('images/home/City')
# 返回: ['images/home/City/city-1.webp', 'images/home/City/city-2.webp', ...]
```

**get_directory_structure(base_path)**
```python
# 获取目录结构
structure = parser.get_directory_structure('images/')
# 返回:
# {
#     'directories': ['home', 'demo-faces', 'options'],
#     'files': []
# }
```

##### 分类方法

**get_files_by_category(category)**
```python
# 获取分类的所有文件
files = parser.get_files_by_category('home')
# 返回: ['images/home/City/city-1.webp', ...]

# 支持的分类:
# - home: 首页图片
# - faces: 人脸图片
# - backdrops: 背景图片
# - poses: 姿势图片
# - outfits: 服装图片
# - hairstyles: 发型图片
# - expressions: 表情图片
# - glasses: 眼镜图片
```

**get_paginated_category(category, page, page_size)**
```python
# 获取分类的分页数据
page_data = parser.get_paginated_category('home', page=1, page_size=20)
# 返回:
# {
#     'category': 'home',
#     'page': 1,
#     'page_size': 20,
#     'total': 288,
#     'total_pages': 15,
#     'items': ['images/home/City/city-1.webp', ...]
# }
```

##### 搜索方法

**search(keyword, case_sensitive)**
```python
# 搜索文件
files = parser.search('blur')
# 返回: ['images/options/backdrops/.../blur-0.webp', ...]

# 区分大小写搜索
files = parser.search('City', case_sensitive=True)
```

## Server 端集成示例

### Flask 示例

```python
from flask import Flask, jsonify, request
from tools.filelist_parser import FileListParser

app = Flask(__name__)

# 初始化解析器
parser = FileListParser('tools/filelist-generator/business-headshot-ai/files.txt')

@app.route('/api/files')
def get_files():
    """获取文件列表（分页）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    data = parser.get_page(page, page_size)
    return jsonify(data)

@app.route('/api/files/<category>')
def get_category_files(category):
    """获取分类文件（分页）"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    
    data = parser.get_paginated_category(category, page, page_size)
    return jsonify(data)

@app.route('/api/search')
def search_files():
    """搜索文件"""
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({'error': 'Missing keyword'}), 400
    
    files = parser.search(keyword)
    return jsonify({
        'keyword': keyword,
        'total': len(files),
        'items': files
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI 示例

```python
from fastapi import FastAPI, Query
from tools.filelist_parser import FileListParser

app = FastAPI()

# 初始化解析器
parser = FileListParser('tools/filelist-generator/business-headshot-ai/files.txt')

@app.get("/api/files")
def get_files(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    """获取文件列表（分页）"""
    return parser.get_page(page, page_size)

@app.get("/api/files/{category}")
def get_category_files(
    category: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """获取分类文件（分页）"""
    return parser.get_paginated_category(category, page, page_size)

@app.get("/api/search")
def search_files(q: str = Query(..., min_length=1)):
    """搜索文件"""
    files = parser.search(q)
    return {
        'keyword': q,
        'total': len(files),
        'items': files
    }
```

## 性能优化

### 1. 二分查找

解析器使用二分查找优化前缀过滤，时间复杂度 O(log n)。

```python
# 利用文件列表已排序的特性
files = parser.filter_by_prefix('images/home/')  # 快速！
```

### 2. 缓存机制

解析器内置缓存，重复查询无需重新过滤。

```python
# 第一次查询：执行过滤
files1 = parser.filter_by_prefix('images/home/')

# 第二次查询：使用缓存
files2 = parser.filter_by_prefix('images/home/')  # 更快！
```

### 3. 内存占用

文件列表全部加载到内存，查询速度极快。

- 1000 个文件 ≈ 50 KB 内存
- 10000 个文件 ≈ 500 KB 内存

## 工作流程

### 开发阶段

```bash
# 1. 添加新图片到 static/business-headshot-ai/images/
cp new-image.webp static/business-headshot-ai/images/home/City/

# 2. 重新生成文件列表
python3 tools/generate-filelist.py business-headshot-ai

# 3. 测试
python3 tools/filelist_parser.py
```

### 部署到生产环境

```bash
# 1. 在本地完成测试
python3 tools/generate-filelist.py business-headshot-ai

# 2. 上传到 S3
aws s3 sync static/business-headshot-ai/ s3://your-bucket/business-headshot-ai/ \
  --exclude "*" \
  --include "images/*" \
  --include "files.txt"

# 3. Server 端从 S3 下载文件列表
aws s3 cp s3://your-bucket/business-headshot-ai/files.txt ./

# 4. Server 端使用解析器
parser = FileListParser('./files.txt')
```

## 与 Manifest 方案对比

| 特性 | 文件列表方案 | Manifest 方案 |
|------|------------|--------------|
| 文件大小 | 极小（~50KB） | 较大（~500KB） |
| 生成速度 | 极快 | 较慢 |
| 灵活性 | 高（server 端控制） | 低（预生成） |
| 元数据 | 动态获取 | 预生成 |
| 维护成本 | 低 | 高 |
| 适用场景 | S3/CDN 模拟 | 完整的 API |

## 常见问题

### Q: 为什么不包含文件大小等元数据？

A: 元数据应该由 server 端动态获取，这样更灵活：
- 文件大小可能变化
- 可以根据需要添加其他元数据
- 保持文件列表精简

### Q: 如何处理文件更新？

A: 重新生成文件列表即可：
```bash
python3 tools/generate-filelist.py business-headshot-ai
```

### Q: 支持多产品吗？

A: 支持！每个产品有独立的文件列表：
```
tools/filelist-generator/business-headshot-ai/files.txt
static/group-photo-ai/files.txt
static/fashion-shot-ai/files.txt
```

### Q: 如何在 server 端获取文件元数据？

A: 使用 Python 的 `os.stat()` 或 `pathlib.Path.stat()`：
```python
from pathlib import Path

file_path = Path('static/business-headshot-ai') / 'images/home/city-1.webp'
stat = file_path.stat()

metadata = {
    'size': stat.st_size,
    'modified': stat.st_mtime,
    'created': stat.st_ctime
}
```

## 总结

这套工具提供了：

- ✅ 精简高效的文件列表格式
- ✅ 快速的解析和查询能力
- ✅ 完整的分页支持
- ✅ 灵活的过滤和搜索
- ✅ 易于集成到 server 端

适合作为 S3/CloudFront 的本地模拟环境使用。
