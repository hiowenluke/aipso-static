#!/usr/bin/env python3
"""
生成静态资源文件列表
只生成文件名列表，不包含其他元数据
输出格式：每行一个相对路径，按字典序排序

版本控制：
- 自动为文件添加版本号参数 ?v=timestamp
- 只有文件内容或修改时间变化时才更新版本号
- 版本号信息存储在 .versions.json 中
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime


def get_file_hash(file_path: Path) -> str:
    """获取文件的 MD5 哈希值（用于检测文件是否变化）"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_versions(output_dir: Path) -> dict:
    """加载版本信息"""
    version_file = output_dir / '.versions.json'
    if version_file.exists():
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_versions(output_dir: Path, versions: dict):
    """保存版本信息"""
    version_file = output_dir / '.versions.json'
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(versions, f, ensure_ascii=False, indent=2)


def generate_filelist(product_slug: str, output_format: str = 'txt', enable_version: bool = True):
    """
    生成产品的文件列表
    
    Args:
        product_slug: 产品 slug，如 'headshot-ai'
        output_format: 输出格式，'txt' 或 'json'
        enable_version: 是否启用版本号
    """
    # 从 tools/filelist-generator/ 往上两级到项目根目录
    base_path = Path(__file__).parent.parent.parent / 'static' / product_slug
    
    if not base_path.exists():
        print(f"❌ 错误: 产品目录不存在: {base_path}")
        return
    
    # 输出目录：tools/filelist-generator/{product_slug}/
    output_dir = Path(__file__).parent / product_slug
    output_dir.mkdir(exist_ok=True)
    
    # 加载版本信息
    versions = load_versions(output_dir) if enable_version else {}
    updated_count = 0
    new_count = 0
    
    # 支持的图片格式
    image_extensions = {'.webp', '.jpg', '.jpeg', '.png', '.gif'}
    
    # 收集所有图片文件
    files = []
    current_files_set = set()  # 用于跟踪当前存在的文件
    current_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    for root, dirs, filenames in os.walk(base_path):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for filename in filenames:
            # 跳过隐藏文件
            if filename.startswith('.'):
                continue
            
            # 检查文件扩展名
            ext = Path(filename).suffix.lower()
            if ext not in image_extensions:
                continue
            
            # 获取相对路径
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(base_path)
            
            # 转换为 POSIX 路径（使用 / 分隔符）
            posix_path = rel_path.as_posix()
            current_files_set.add(posix_path)  # 记录当前存在的文件
            
            if enable_version:
                # 计算文件哈希
                file_hash = get_file_hash(file_path)
                
                # 检查是否需要更新版本号
                if posix_path in versions:
                    old_hash = versions[posix_path].get('hash')
                    if old_hash != file_hash:
                        # 文件已变化，更新版本号
                        versions[posix_path] = {
                            'hash': file_hash,
                            'version': current_timestamp
                        }
                        updated_count += 1
                else:
                    # 新文件
                    versions[posix_path] = {
                        'hash': file_hash,
                        'version': current_timestamp
                    }
                    new_count += 1
                
                # 添加版本号参数
                version = versions[posix_path]['version']
                posix_path_with_version = f"{posix_path}?v={version}"
                files.append(posix_path_with_version)
            else:
                files.append(posix_path)
    
    # 排序
    files.sort()
    
    # 清理已删除文件的版本信息
    if enable_version:
        deleted_count = 0
        files_to_delete = []
        for file_path in versions.keys():
            if file_path not in current_files_set:
                files_to_delete.append(file_path)
                deleted_count += 1
        
        for file_path in files_to_delete:
            del versions[file_path]
        
        if deleted_count > 0:
            print(f"🗑️  清理已删除文件: {deleted_count} 个")
        
        save_versions(output_dir, versions)
    
    if output_format == 'txt':
        output_file = output_dir / 'files.txt'
        with open(output_file, 'w', encoding='utf-8') as f:
            for file_path in files:
                f.write(f"{file_path}\n")
        
        print(f"✅ 已生成文件列表: {output_file}")
        print(f"📊 总计 {len(files)} 个文件")
        if enable_version:
            print(f"🆕 新增文件: {new_count} 个")
            print(f"🔄 更新文件: {updated_count} 个")
        print(f"💾 文件大小: {output_file.stat().st_size / 1024:.2f} KB")
    
    elif output_format == 'json':
        output_file = output_dir / 'files.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=None)
        
        print(f"✅ 已生成文件列表: {output_file}")
        print(f"📊 总计 {len(files)} 个文件")
        if enable_version:
            print(f"🆕 新增文件: {new_count} 个")
            print(f"🔄 更新文件: {updated_count} 个")
        print(f"💾 文件大小: {output_file.stat().st_size / 1024:.2f} KB")
    
    return files


def generate_all_products(output_format: str = 'txt'):
    """生成所有产品的文件列表"""
    # 从 tools/filelist-generator/ 往上两级到项目根目录
    store_dir = Path(__file__).parent.parent.parent / 'static'
    
    if not store_dir.exists():
        print("❌ static 目录不存在")
        return
    
    products = []
    for item in store_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            products.append(item.name)
    
    if not products:
        print("❌ 未找到任何产品目录")
        return
    
    print("=" * 60)
    print("📦 静态资源文件列表生成工具")
    print("=" * 60)
    print()
    
    for product in products:
        print(f"处理产品: {product}")
        generate_filelist(product, output_format)
        print()
    
    print("=" * 60)
    print("✅ 所有文件列表生成完成！")
    print("=" * 60)


def main():
    import sys
    
    if len(sys.argv) > 1:
        product_slug = sys.argv[1]
        output_format = sys.argv[2] if len(sys.argv) > 2 else 'txt'
        
        print("=" * 60)
        print("📦 静态资源文件列表生成工具")
        print("=" * 60)
        print()
        
        generate_filelist(product_slug, output_format)
        
        print()
        print("=" * 60)
    else:
        # 生成所有产品
        generate_all_products('txt')


if __name__ == '__main__':
    main()
