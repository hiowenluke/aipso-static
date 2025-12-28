"""
1. 读取输入文件夹"static/headshot-ai/images/options/backdrops"。
2. 遍历其下第一级子文件夹。
  - 遍历再下一级子文件夹，将名字中"@"及后面的字符串删除。

用法：
python backdrops_rename_filenames.py
python backdrops_rename_filenames.py ./custom/path
"""
import sys
from pathlib import Path


def rename_folders(base_path="static/headshot-ai/images/options/backdrops"):
    """重命名文件夹，删除 @ 及后面的字符串"""
    base_dir = Path(base_path)
    
    if not base_dir.exists():
        print(f"错误：目录 {base_dir} 不存在！")
        return
    
    if not base_dir.is_dir():
        print(f"错误：{base_dir} 不是一个目录！")
        return
    
    print(f"开始处理目录: {base_dir}")
    renamed_count = 0
    
    # 遍历第一级子文件夹
    for first_level in base_dir.iterdir():
        if not first_level.is_dir():
            continue
        
        print(f"\n处理第一级文件夹: {first_level.name}")
        
        # 遍历第二级子文件夹
        for second_level in first_level.iterdir():
            if not second_level.is_dir():
                continue
            
            # 检查文件夹名是否包含 @
            if "@" in second_level.name:
                # 删除 @ 及后面的字符串
                new_name = second_level.name.split("@")[0]
                new_path = second_level.parent / new_name
                
                # 检查新名称是否已存在
                if new_path.exists():
                    print(f"  跳过: {second_level.name} -> {new_name} (目标已存在)")
                    continue
                
                # 重命名
                second_level.rename(new_path)
                print(f"  重命名: {second_level.name} -> {new_name}")
                renamed_count += 1
            else:
                print(f"  跳过: {second_level.name} (无需重命名)")
    
    print(f"\n处理完成！共重命名 {renamed_count} 个文件夹。")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
        print(f"使用自定义路径: {custom_path}")
        rename_folders(custom_path)
    else:
        print("使用默认路径: static/headshot-ai/images/options/backdrops")
        rename_folders()
