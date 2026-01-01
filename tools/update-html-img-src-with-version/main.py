"""
更新 static 目录下所有 HTML 文件的图片 src，添加版本号

功能：
1. 遍历 static 文件夹下的所有一级子文件夹
2. 对每个子文件夹：
   - 读取 tools/filelist-generator/{子文件夹名}/files.txt
   - 遍历该子文件夹下的所有 HTML 文件（递归）
   - 用 files.txt 里的 URL（带版本号）替换 HTML 中的图片 src

用法：
python tools/update-html-img-src-with-version/main.py
python tools/update-html-img-src-with-version/main.py business-headshot-ai  # 只处理指定产品
"""

import re
import sys
from pathlib import Path


def load_file_versions(files_txt_path: Path) -> dict:
    """加载文件版本映射"""
    if not files_txt_path.exists():
        print(f"❌ 错误: files.txt 不存在: {files_txt_path}")
        return {}
    
    version_map = {}
    
    with open(files_txt_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # 解析 URL：/images-step1/demo-1.webp?v=20231217_143025
            if '?v=' in line:
                file_path, version = line.split('?v=')
                # 只保留文件名部分作为 key
                # /images-step1/demo-1.webp -> images-step1/demo-1.webp
                file_path = file_path.lstrip('/')
                version_map[file_path] = f"?v={version}"
            else:
                # 没有版本号的情况
                file_path = line.lstrip('/')
                version_map[file_path] = ""
    
    return version_map


def update_html_file(html_path: Path, version_map: dict, product_dir: Path) -> bool:
    """更新单个 HTML 文件中的图片 src"""
    if not html_path.exists():
        print(f"❌ HTML 文件不存在: {html_path}")
        return False
    
    # 计算 HTML 文件相对于产品目录的路径
    # 例如: first-popup/female/White/young/slim/
    html_relative_dir = html_path.parent.relative_to(product_dir)
    
    # 读取 HTML 内容
    content = html_path.read_text(encoding='utf-8')
    original_content = content
    
    # 匹配 src="./xxx" 或 src='./xxx'
    # 使用正则表达式查找所有图片 src
    def replace_src(match):
        quote = match.group(1)  # 引号类型（" 或 '）
        src_path = match.group(2)  # 原始路径
        
        # 移除 ./ 前缀和已有的版本号
        clean_path = src_path.lstrip('./')
        if '?v=' in clean_path:
            clean_path = clean_path.split('?v=')[0]
        
        # 构建完整路径：HTML 所在目录 + 相对路径
        # 例如: first-popup/female/White/young/slim/ + images-step1/demo-1.webp
        full_path = (html_relative_dir / clean_path).as_posix()
        
        # 查找对应的版本号
        if full_path in version_map:
            version = version_map[full_path]
            new_src = f"./{clean_path}{version}"
            return f'src={quote}{new_src}{quote}'
        else:
            # 没有找到版本号，保持原样
            return match.group(0)
    
    # 替换所有 src 属性
    pattern = r'src=(["\'])(\./[^"\']+)\1'
    content = re.sub(pattern, replace_src, content)
    
    # 检查是否有变化
    if content != original_content:
        html_path.write_text(content, encoding='utf-8')
        return True
    
    return False


def process_product(product_name: str, base_dir: Path) -> dict:
    """处理单个产品目录"""
    result = {
        'product': product_name,
        'html_files': 0,
        'updated_files': 0,
        'skipped_files': 0,
        'error': None
    }
    
    # 路径
    files_txt = base_dir / 'tools' / 'filelist-generator' / product_name / 'files.txt'
    product_dir = base_dir / 'static' / product_name
    
    # 检查 files.txt 是否存在
    if not files_txt.exists():
        result['error'] = f"files.txt 不存在"
        return result
    
    # 检查产品目录是否存在
    if not product_dir.exists():
        result['error'] = f"产品目录不存在"
        return result
    
    # 加载版本映射
    version_map = load_file_versions(files_txt)
    
    if not version_map:
        result['error'] = f"未找到版本信息"
        return result
    
    # 递归查找所有 HTML 文件
    html_files = list(product_dir.rglob('*.html'))
    
    if not html_files:
        result['error'] = f"未找到 HTML 文件"
        return result
    
    result['html_files'] = len(html_files)
    
    # 更新每个 HTML 文件
    for html_file in html_files:
        if update_html_file(html_file, version_map, product_dir):
            result['updated_files'] += 1
        else:
            result['skipped_files'] += 1
    
    return result


def main():
    """主函数"""
    print("=" * 60)
    print("🔄 更新 HTML 文件图片 src 版本号")
    print("=" * 60)
    print()
    
    # 路径配置
    base_dir = Path(__file__).parent.parent.parent
    static_dir = base_dir / 'static'
    
    # 检查 static 目录
    if not static_dir.exists():
        print(f"❌ 错误: static 目录不存在: {static_dir}")
        return
    
    # 获取要处理的产品列表
    if len(sys.argv) > 1:
        # 处理指定的产品
        products = [sys.argv[1]]
        print(f"📦 处理指定产品: {products[0]}")
    else:
        # 处理所有产品
        products = []
        for item in static_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                products.append(item.name)
        
        if not products:
            print("❌ 错误: 未找到任何产品目录")
            return
        
        print(f"📦 找到 {len(products)} 个产品目录")
    
    print()
    
    # 处理每个产品
    results = []
    total_html = 0
    total_updated = 0
    total_skipped = 0
    
    for product_name in products:
        print(f"{'='*60}")
        print(f"📁 处理产品: {product_name}")
        print(f"{'='*60}")
        
        result = process_product(product_name, base_dir)
        results.append(result)
        
        if result['error']:
            print(f"⚠️  {result['error']}")
        else:
            print(f"✅ HTML 文件: {result['html_files']} 个")
            print(f"   更新: {result['updated_files']} 个")
            print(f"   跳过: {result['skipped_files']} 个")
            
            total_html += result['html_files']
            total_updated += result['updated_files']
            total_skipped += result['skipped_files']
        
        print()
    
    # 总结
    print("=" * 60)
    print("📊 处理总结")
    print("=" * 60)
    
    success_count = sum(1 for r in results if not r['error'])
    error_count = sum(1 for r in results if r['error'])
    
    print(f"✅ 成功处理: {success_count} 个产品")
    if error_count > 0:
        print(f"⚠️  跳过: {error_count} 个产品")
    print(f"📝 HTML 文件总计: {total_html} 个")
    print(f"🔄 更新: {total_updated} 个")
    print(f"⏭️  跳过: {total_skipped} 个")
    
    # 显示错误详情
    if error_count > 0:
        print()
        print("⚠️  跳过的产品:")
        for result in results:
            if result['error']:
                print(f"   • {result['product']}: {result['error']}")
    
    print("=" * 60)


if __name__ == '__main__':
    main()
