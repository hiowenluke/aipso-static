#!/usr/bin/env python3
"""
将 static 目录下的所有文件和文件夹重命名为小写

功能：
1. 递归遍历指定目录
2. 将所有文件名和文件夹名转换为小写（包括扩展名）
3. 使用两阶段重命名避免大小写冲突：
   - 第一阶段：添加临时后缀 "-tmp-rename"
   - 第二阶段：转为小写并移除后缀
4. 提供预览模式（不实际重命名）

示例转换：
- Dark-Brown.WEBP -> Dark-Brown-tmp-rename.WEBP -> dark-brown.webp
- Female-White/ -> Female-White-tmp-rename/ -> female-white/

用法：
python tools/static_filenames_to_lowercase.py                    # 预览模式
python tools/static_filenames_to_lowercase.py --apply            # 实际执行
python tools/static_filenames_to_lowercase.py headshot-ai        # 只处理指定产品
python tools/static_filenames_to_lowercase.py headshot-ai --apply
"""

import sys
from pathlib import Path


TEMP_SUFFIX = "-tmp-rename"


def rename_to_lowercase(base_path: Path, dry_run: bool = True) -> dict:
    """
    两阶段重命名文件和文件夹为小写
    
    阶段1: 添加临时后缀
    阶段2: 转为小写并移除后缀
    
    Args:
        base_path: 基础路径
        dry_run: True 为预览模式，False 为实际执行
    
    Returns:
        统计信息字典
    """
    stats = {
        'files_renamed': 0,
        'dirs_renamed': 0,
        'files_skipped': 0,
        'dirs_skipped': 0,
        'errors': []
    }
    
    # 收集所有需要重命名的项目
    items_to_rename = []
    
    for item in base_path.rglob('*'):
        # 跳过隐藏文件和文件夹
        if item.name.startswith('.'):
            continue
        
        # 跳过已经是小写的
        lower_name = item.name.lower()
        if lower_name == item.name:
            continue
        
        items_to_rename.append(item)
    
    if not items_to_rename:
        print("  ✅ 所有文件名已经是小写，无需处理")
        return stats
    
    # 按路径深度排序（深的先处理）
    items_to_rename.sort(key=lambda x: len(x.parts), reverse=True)
    
    print(f"  📝 找到 {len(items_to_rename)} 个需要重命名的项目\n")
    
    # ========== 阶段 1: 添加临时后缀 ==========
    print("  🔄 阶段 1: 添加临时后缀...\n")
    
    phase1_mapping = {}  # 记录原始路径 -> 临时路径的映射
    
    for item in items_to_rename:
        # 构建临时名称
        if item.is_file():
            # 文件：在扩展名前添加后缀
            stem = item.stem
            suffix = item.suffix
            temp_name = f"{stem}{TEMP_SUFFIX}{suffix}"
        else:
            # 文件夹：直接添加后缀
            temp_name = f"{item.name}{TEMP_SUFFIX}"
        
        temp_path = item.parent / temp_name
        item_type = "文件" if item.is_file() else "文件夹"
        
        if dry_run:
            print(f"    [预览] {item_type}: {item.name} -> {temp_name}")
            phase1_mapping[str(item)] = (temp_path, item.name.lower(), item.is_file())
        else:
            try:
                item.rename(temp_path)
                print(f"    ✅ {item_type}: {item.name} -> {temp_name}")
                phase1_mapping[str(item)] = (temp_path, item.name.lower(), item.is_file())
            except Exception as e:
                error_msg = f"阶段1错误: {item.name} -> {temp_name}: {e}"
                stats['errors'].append(error_msg)
                print(f"    ❌ {error_msg}")
                
                if item.is_file():
                    stats['files_skipped'] += 1
                else:
                    stats['dirs_skipped'] += 1
    
    print(f"\n  ✅ 阶段 1 完成: {len(phase1_mapping)} 个项目\n")
    
    # ========== 阶段 2: 转为小写并移除后缀 ==========
    print("  🔄 阶段 2: 转为小写并移除后缀...\n")
    
    # 重新扫描，找到所有带临时后缀的文件
    # 这样可以处理父目录改名后的路径变化
    temp_items = []
    for item in base_path.rglob(f'*{TEMP_SUFFIX}*'):
        if item.name.startswith('.'):
            continue
        temp_items.append(item)
    
    # 按路径深度排序（深的先处理）
    temp_items.sort(key=lambda x: len(x.parts), reverse=True)
    
    for temp_item in temp_items:
        # 计算最终的小写名称（移除临时后缀）
        if temp_item.is_file():
            # 文件：移除扩展名前的后缀
            stem = temp_item.stem.replace(TEMP_SUFFIX, '')
            suffix = temp_item.suffix
            final_name = f"{stem}{suffix}".lower()
        else:
            # 文件夹：移除后缀
            final_name = temp_item.name.replace(TEMP_SUFFIX, '').lower()
        
        final_path = temp_item.parent / final_name
        item_type = "文件" if temp_item.is_file() else "文件夹"
        
        if dry_run:
            print(f"    [预览] {item_type}: {temp_item.name} -> {final_name}")
            
            if temp_item.is_file():
                stats['files_renamed'] += 1
            else:
                stats['dirs_renamed'] += 1
        else:
            try:
                temp_item.rename(final_path)
                print(f"    ✅ {item_type}: {temp_item.name} -> {final_name}")
                
                if temp_item.is_file():
                    stats['files_renamed'] += 1
                else:
                    stats['dirs_renamed'] += 1
            except Exception as e:
                error_msg = f"阶段2错误: {temp_item.name} -> {final_name}: {e}"
                stats['errors'].append(error_msg)
                print(f"    ❌ {error_msg}")
                print(f"    ⚠️  请手动处理: {temp_item}")
                
                if temp_item.is_file():
                    stats['files_skipped'] += 1
                else:
                    stats['dirs_skipped'] += 1
    
    print(f"\n  ✅ 阶段 2 完成\n")
    
    return stats


def process_product(product_name: str, base_dir: Path, dry_run: bool = True):
    """处理单个产品"""
    product_path = base_dir / 'static' / product_name
    
    if not product_path.exists():
        print(f"❌ 错误: 产品目录不存在: {product_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"📁 {'预览' if dry_run else '处理'}产品: {product_name}")
    print(f"{'='*60}\n")
    
    # 执行两阶段重命名
    stats = rename_to_lowercase(product_path, dry_run)
    
    # 显示统计
    print(f"{'='*60}")
    print(f"📊 统计信息")
    print(f"{'='*60}")
    
    if dry_run:
        total = stats['files_renamed'] + stats['dirs_renamed']
        if total > 0:
            print(f"📝 预计重命名:")
            print(f"   文件: {stats['files_renamed']} 个")
            print(f"   文件夹: {stats['dirs_renamed']} 个")
            print(f"   总计: {total} 个")
        else:
            print(f"✅ 无需重命名")
    else:
        print(f"✅ 已重命名:")
        print(f"   文件: {stats['files_renamed']} 个")
        print(f"   文件夹: {stats['dirs_renamed']} 个")
        
        if stats['files_skipped'] > 0 or stats['dirs_skipped'] > 0:
            print(f"⏭️  跳过:")
            print(f"   文件: {stats['files_skipped']} 个")
            print(f"   文件夹: {stats['dirs_skipped']} 个")
    
    if stats['errors']:
        print(f"\n❌ 错误 ({len(stats['errors'])} 个):")
        for error in stats['errors']:
            print(f"   • {error}")
    
    print(f"{'='*60}\n")
    
    if dry_run:
        print("💡 提示: 使用 --apply 参数执行实际重命名")


def main():
    """主函数"""
    # 解析参数
    args = sys.argv[1:]
    dry_run = '--apply' not in args
    
    # 移除 --apply 参数
    args = [arg for arg in args if arg != '--apply']
    
    # 获取产品名称
    product_name = args[0] if args else None
    
    # 基础路径
    base_dir = Path(__file__).parent.parent
    
    print("=" * 60)
    print(f"🔤 文件名转小写工具 {'[预览模式]' if dry_run else '[执行模式]'}")
    print("=" * 60)
    
    if product_name:
        # 处理指定产品
        process_product(product_name, base_dir, dry_run)
    else:
        # 处理所有产品
        static_dir = base_dir / 'static'
        
        if not static_dir.exists():
            print(f"❌ 错误: static 目录不存在: {static_dir}")
            return
        
        products = []
        for item in static_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                products.append(item.name)
        
        if not products:
            print("❌ 错误: 未找到任何产品目录")
            return
        
        print(f"\n📦 找到 {len(products)} 个产品目录\n")
        
        for product in products:
            process_product(product, base_dir, dry_run)
        
        print("=" * 60)
        print("✅ 所有产品处理完成")
        print("=" * 60)


if __name__ == '__main__':
    main()
