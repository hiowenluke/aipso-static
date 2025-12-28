#!/usr/bin/env python3
"""
文件监视和同步工具
监视 static/ 目录的变化，自动生成文件列表并同步到 server 端
"""

import sys
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# 配置
STORE_DIR = Path(__file__).parent.parent.parent / 'static'
FILELIST_GENERATOR = Path(__file__).parent.parent / 'filelist-generator' / 'generate-filelist.py'
FILELIST_OUTPUT_DIR = Path(__file__).parent.parent / 'filelist-generator'
SERVER_STORE_DIR = Path('/Users/luyunfei/Desktop/________/____AI 摄影/____aipso-app/aipso-server/static')

# 支持的图片格式
IMAGE_EXTENSIONS = {'.webp', '.jpg', '.jpeg', '.png', '.gif'}

# 防抖动：避免短时间内重复触发
DEBOUNCE_SECONDS = 2
last_trigger_time = {}


class StoreFileHandler(FileSystemEventHandler):
    """Store 目录文件变化处理器"""
    
    def __init__(self):
        super().__init__()
        self.processing = set()
    
    def on_any_event(self, event):
        """处理任何文件系统事件"""
        # 忽略目录事件
        if event.is_directory:
            return
        
        # 只处理图片文件
        file_path = Path(event.src_path)
        if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            return
        
        # 判断是哪个产品
        try:
            relative_path = file_path.relative_to(STORE_DIR)
            product_slug = relative_path.parts[0]
        except (ValueError, IndexError):
            return
        
        # 防抖动：避免短时间内重复触发
        current_time = time.time()
        if product_slug in last_trigger_time:
            if current_time - last_trigger_time[product_slug] < DEBOUNCE_SECONDS:
                return
        
        last_trigger_time[product_slug] = current_time
        
        # 避免重复处理
        if product_slug in self.processing:
            return
        
        # 处理变化
        self.processing.add(product_slug)
        try:
            self.handle_change(product_slug, event)
        finally:
            self.processing.discard(product_slug)
    
    def handle_change(self, product_slug: str, event):
        """处理文件变化"""
        event_type = event.event_type
        file_path = Path(event.src_path)
        
        print(f"\n{'='*60}")
        print(f"📁 检测到变化: {product_slug}")
        print(f"   事件类型: {event_type}")
        print(f"   文件: {file_path.name}")
        print(f"{'='*60}")
        
        # 1. 生成文件列表
        print(f"\n🔄 步骤 1: 生成文件列表...")
        try:
            result = subprocess.run(
                [sys.executable, str(FILELIST_GENERATOR), product_slug],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ 文件列表生成成功")
                # 显示输出（去掉分隔线）
                for line in result.stdout.split('\n'):
                    if line and not line.startswith('='):
                        print(f"   {line}")
            else:
                print(f"❌ 文件列表生成失败")
                print(result.stderr)
                return
        except subprocess.TimeoutExpired:
            print(f"❌ 生成超时")
            return
        except Exception as e:
            print(f"❌ 生成错误: {e}")
            return
        
        # 2. 同步到 server 端
        print(f"\n🔄 步骤 2: 同步到 server 端...")
        source_file = FILELIST_OUTPUT_DIR / product_slug / 'files.txt'
        target_dir = SERVER_STORE_DIR / product_slug
        target_file = target_dir / 'files.txt'
        
        if not source_file.exists():
            print(f"❌ 源文件不存在: {source_file}")
            return
        
        # 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            shutil.copy2(source_file, target_file)
            print(f"✅ 同步成功")
            print(f"   源: {source_file}")
            print(f"   目标: {target_file}")
            
            # 显示文件大小
            size_kb = target_file.stat().st_size / 1024
            print(f"   大小: {size_kb:.2f} KB")
        except Exception as e:
            print(f"❌ 同步失败: {e}")
            return
        
        print(f"\n{'='*60}")
        print(f"✅ 处理完成: {product_slug}")
        print(f"{'='*60}\n")


def check_dependencies():
    """检查依赖"""
    try:
        import watchdog
        return True
    except ImportError:
        print("❌ 缺少依赖: watchdog")
        print("\n请安装依赖:")
        print("  pip install watchdog")
        print("\n或者:")
        print("  pip3 install watchdog")
        return False


def check_paths():
    """检查路径"""
    errors = []
    
    if not STORE_DIR.exists():
        errors.append(f"Store 目录不存在: {STORE_DIR}")
    
    if not FILELIST_GENERATOR.exists():
        errors.append(f"生成器脚本不存在: {FILELIST_GENERATOR}")
    
    if not SERVER_STORE_DIR.exists():
        errors.append(f"Server static 目录不存在: {SERVER_STORE_DIR}")
    
    if errors:
        print("❌ 路径检查失败:\n")
        for error in errors:
            print(f"   • {error}")
        print("\n请检查配置并修正路径")
        return False
    
    return True


def check_and_generate_missing_filelists():
    """检查并生成缺失的 files.txt"""
    print("🔍 检查 files.txt 是否存在...\n")
    
    # 获取所有产品
    products = []
    for item in STORE_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            products.append(item.name)
    
    if not products:
        print("⚠️  未找到任何产品目录\n")
        return
    
    generated_count = 0
    
    for product_slug in products:
        files_txt = FILELIST_OUTPUT_DIR / product_slug / 'files.txt'
        
        if not files_txt.exists():
            print(f"📝 {product_slug}: files.txt 不存在，正在生成...")
            
            try:
                result = subprocess.run(
                    [sys.executable, str(FILELIST_GENERATOR), product_slug],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"   ✅ 生成成功")
                    generated_count += 1
                    
                    # 同步到 server 端
                    source_file = FILELIST_OUTPUT_DIR / product_slug / 'files.txt'
                    target_dir = SERVER_STORE_DIR / product_slug
                    target_file = target_dir / 'files.txt'
                    
                    if source_file.exists():
                        target_dir.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, target_file)
                        print(f"   ✅ 已同步到 server 端")
                else:
                    print(f"   ❌ 生成失败: {result.stderr}")
            except Exception as e:
                print(f"   ❌ 错误: {e}")
        else:
            print(f"✅ {product_slug}: files.txt 已存在")
    
    if generated_count > 0:
        print(f"\n🎉 已生成 {generated_count} 个缺失的 files.txt\n")
    else:
        print(f"\n✅ 所有 files.txt 都已存在\n")
    
    print("=" * 60)
    print()


def main():
    """主函数"""
    print("=" * 60)
    print("🔍 文件监视和同步工具")
    print("=" * 60)
    print()
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查路径
    if not check_paths():
        sys.exit(1)
    
    print(f"📁 监视目录: {STORE_DIR}")
    print(f"📝 生成器: {FILELIST_GENERATOR}")
    print(f"🎯 同步目标: {SERVER_STORE_DIR}")
    print()
    print("💡 提示:")
    print("   • 当 static/ 目录下的图片文件发生变化时")
    print("   • 自动生成文件列表")
    print("   • 自动同步到 server 端")
    print("   • 使用 Ctrl+C 停止监视")
    print()
    print("=" * 60)
    print()
    
    # 启动前检查并生成缺失的 files.txt
    check_and_generate_missing_filelists()
    
    # 创建事件处理器和观察者
    event_handler = StoreFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(STORE_DIR), recursive=True)
    
    # 启动观察者
    observer.start()
    print("✅ 监视已启动，等待文件变化...\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 停止监视...")
        observer.stop()
    
    observer.join()
    print("👋 已退出\n")


if __name__ == '__main__':
    main()
