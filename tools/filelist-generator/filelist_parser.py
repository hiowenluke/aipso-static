"""
文件列表解析器
提供快速解析和分页功能，供 server 端使用
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import bisect


class FileListParser:
    """文件列表解析器"""
    
    def __init__(self, filelist_path: str):
        """
        初始化解析器
        
        Args:
            filelist_path: 文件列表路径，如 'tools/filelist-generator/headshot-ai/files.txt'
        """
        self.filelist_path = Path(filelist_path)
        self._files: List[str] = []
        self._index_cache: Dict[str, List[str]] = {}
        self._load_files()
    
    def _load_files(self):
        """加载文件列表"""
        if not self.filelist_path.exists():
            raise FileNotFoundError(f"文件列表不存在: {self.filelist_path}")
        
        with open(self.filelist_path, 'r', encoding='utf-8') as f:
            self._files = [line.strip() for line in f if line.strip()]
    
    def get_all_files(self) -> List[str]:
        """获取所有文件"""
        return self._files.copy()
    
    def get_total_count(self) -> int:
        """获取文件总数"""
        return len(self._files)
    
    def get_page(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        获取分页数据
        
        Args:
            page: 页码（从 1 开始）
            page_size: 每页数量
        
        Returns:
            {
                'page': 当前页码,
                'page_size': 每页数量,
                'total': 总数,
                'total_pages': 总页数,
                'items': 文件列表
            }
        """
        total = len(self._files)
        total_pages = (total + page_size - 1) // page_size
        
        # 边界检查
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages if total_pages > 0 else 1
        
        # 计算起始和结束索引
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        
        return {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages,
            'items': self._files[start:end]
        }
    
    def filter_by_prefix(self, prefix: str) -> List[str]:
        """
        按路径前缀过滤文件
        
        Args:
            prefix: 路径前缀，如 'images/home/'
        
        Returns:
            匹配的文件列表
        """
        # 使用缓存
        if prefix in self._index_cache:
            return self._index_cache[prefix].copy()
        
        # 二分查找起始位置
        start_idx = bisect.bisect_left(self._files, prefix)
        
        # 收集匹配的文件
        result = []
        for i in range(start_idx, len(self._files)):
            if self._files[i].startswith(prefix):
                result.append(self._files[i])
            else:
                break
        
        # 缓存结果
        self._index_cache[prefix] = result.copy()
        
        return result
    
    def filter_by_directory(self, directory: str) -> List[str]:
        """
        按目录过滤文件（不包含子目录）
        
        Args:
            directory: 目录路径，如 'images/home/City'
        
        Returns:
            该目录下的文件列表（不包含子目录）
        """
        # 确保目录路径以 / 结尾
        if not directory.endswith('/'):
            directory += '/'
        
        result = []
        for file_path in self._files:
            if file_path.startswith(directory):
                # 检查是否在子目录中
                relative = file_path[len(directory):]
                if '/' not in relative:
                    result.append(file_path)
        
        return result
    
    def get_directory_structure(self, base_path: str = '') -> Dict[str, Any]:
        """
        获取目录结构
        
        Args:
            base_path: 基础路径，如 'images/'
        
        Returns:
            {
                'directories': ['dir1', 'dir2', ...],
                'files': ['file1.webp', 'file2.webp', ...]
            }
        """
        if base_path and not base_path.endswith('/'):
            base_path += '/'
        
        directories = set()
        files = []
        
        for file_path in self._files:
            if not file_path.startswith(base_path):
                continue
            
            relative = file_path[len(base_path):]
            
            if '/' in relative:
                # 这是一个子目录中的文件
                dir_name = relative.split('/')[0]
                directories.add(dir_name)
            else:
                # 这是当前目录的文件
                files.append(relative)
        
        return {
            'directories': sorted(directories),
            'files': sorted(files)
        }
    
    def search(self, keyword: str, case_sensitive: bool = False) -> List[str]:
        """
        搜索文件
        
        Args:
            keyword: 搜索关键词
            case_sensitive: 是否区分大小写
        
        Returns:
            匹配的文件列表
        """
        if not case_sensitive:
            keyword = keyword.lower()
        
        result = []
        for file_path in self._files:
            search_target = file_path if case_sensitive else file_path.lower()
            if keyword in search_target:
                result.append(file_path)
        
        return result
    
    def get_files_by_category(self, category: str) -> List[str]:
        """
        按分类获取文件（基于目录结构）
        
        Args:
            category: 分类名称，如 'home', 'faces', 'backdrops'
        
        Returns:
            该分类下的所有文件
        """
        # 常见的分类路径映射
        category_paths = {
            'home': 'images/home/',
            'faces': 'images/demo-faces/',
            'backdrops': 'images/options/backdrops/',
            'poses': 'images/options/poses/',
            'outfits': 'images/options/outfits/',
            'hairstyles': 'images/options/hairstyles/',
            'expressions': 'images/options/expressions/',
            'glasses': 'images/options/glasses/',
        }
        
        prefix = category_paths.get(category, f'images/{category}/')
        return self.filter_by_prefix(prefix)
    
    def get_paginated_category(self, category: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        获取分类的分页数据
        
        Args:
            category: 分类名称
            page: 页码
            page_size: 每页数量
        
        Returns:
            分页数据
        """
        files = self.get_files_by_category(category)
        total = len(files)
        total_pages = (total + page_size - 1) // page_size
        
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages if total_pages > 0 else 1
        
        start = (page - 1) * page_size
        end = min(start + page_size, total)
        
        return {
            'category': category,
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': total_pages,
            'items': files[start:end]
        }


# ==================== 使用示例 ====================

def example_usage():
    """使用示例"""
    
    # 初始化解析器
    parser = FileListParser('tools/filelist-generator/headshot-ai/files.txt')
    
    print("=" * 60)
    print("文件列表解析器 - 使用示例")
    print("=" * 60)
    print()
    
    # 1. 获取总数
    print(f"📊 总文件数: {parser.get_total_count()}")
    print()
    
    # 2. 获取分页数据
    print("📄 第 1 页数据:")
    page_data = parser.get_page(page=1, page_size=10)
    print(f"   页码: {page_data['page']}/{page_data['total_pages']}")
    print(f"   总数: {page_data['total']}")
    print(f"   文件:")
    for item in page_data['items'][:3]:
        print(f"      - {item}")
    print(f"      ... (共 {len(page_data['items'])} 个)")
    print()
    
    # 3. 按前缀过滤
    print("🔍 过滤 'images/home/' 目录:")
    home_files = parser.filter_by_prefix('images/home/')
    print(f"   找到 {len(home_files)} 个文件")
    if home_files:
        print(f"   示例: {home_files[0]}")
    print()
    
    # 4. 获取目录结构
    print("📁 'images/' 目录结构:")
    structure = parser.get_directory_structure('images/')
    print(f"   子目录: {structure['directories'][:5]}")
    print(f"   文件数: {len(structure['files'])}")
    print()
    
    # 5. 按分类获取
    print("🏠 获取 'home' 分类:")
    home_category = parser.get_paginated_category('home', page=1, page_size=5)
    print(f"   总数: {home_category['total']}")
    print(f"   页数: {home_category['total_pages']}")
    print(f"   文件:")
    for item in home_category['items'][:3]:
        print(f"      - {item}")
    print()
    
    # 6. 搜索
    print("🔎 搜索包含 'blur' 的文件:")
    search_results = parser.search('blur')
    print(f"   找到 {len(search_results)} 个文件")
    if search_results:
        print(f"   示例: {search_results[0]}")
    print()
    
    print("=" * 60)


if __name__ == '__main__':
    example_usage()
