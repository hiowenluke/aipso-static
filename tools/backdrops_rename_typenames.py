"""
读取文件夹"static/business-headshot-ai/images/options/backdrops/"：
- 将 "03@studio-blue" 重命名为 "02@studio-blue"
- 将 "02@studio-gray" 重命名为 "03@studio-gray"

用法：
python backdrops_rename_typenames.py
python backdrops_rename_typenames.py ./custom/path
"""
import sys
from pathlib import Path


def rename_type_folders(base_path="static/business-headshot-ai/images/options/backdrops"):
    """重命名特定的类型文件夹"""
    base_dir = Path(base_path)
    
    if not base_dir.exists():
        print(f"错误：目录 {base_dir} 不存在！")
        return
    
    if not base_dir.is_dir():
        print(f"错误：{base_dir} 不是一个目录！")
        return
    
    print(f"开始处理目录: {base_dir}")
    
    # 定义重命名映射
    rename_map = {
        "03@studio-blue": "02@studio-blue",
        "02@studio-gray": "03@studio-gray"
    }
    
    # 为了避免冲突，需要使用临时名称
    # 步骤：03@studio-blue -> temp -> 02@studio-blue
    #       02@studio-gray -> 03@studio-gray
    
    temp_name = "_temp_rename_"
    renamed_count = 0
    
    # 第一步：将 03@studio-blue 重命名为临时名称
    source_1 = base_dir / "03@studio-blue"
    temp_path = base_dir / temp_name
    
    if source_1.exists():
        source_1.rename(temp_path)
        print(f"临时重命名: 03@studio-blue -> {temp_name}")
    else:
        print(f"警告: 03@studio-blue 不存在")
        temp_path = None
    
    # 第二步：将 02@studio-gray 重命名为 03@studio-gray
    source_2 = base_dir / "02@studio-gray"
    target_2 = base_dir / "03@studio-gray"
    
    if source_2.exists():
        if target_2.exists():
            print(f"错误: 目标 03@studio-gray 已存在，无法重命名")
        else:
            source_2.rename(target_2)
            print(f"重命名: 02@studio-gray -> 03@studio-gray")
            renamed_count += 1
    else:
        print(f"警告: 02@studio-gray 不存在")
    
    # 第三步：将临时名称重命名为 02@studio-blue
    if temp_path and temp_path.exists():
        target_1 = base_dir / "02@studio-blue"
        if target_1.exists():
            print(f"错误: 目标 02@studio-blue 已存在，无法重命名")
        else:
            temp_path.rename(target_1)
            print(f"重命名: 03@studio-blue -> 02@studio-blue")
            renamed_count += 1
    
    print(f"\n处理完成！共重命名 {renamed_count} 个文件夹。")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        custom_path = sys.argv[1]
        print(f"使用自定义路径: {custom_path}")
        rename_type_folders(custom_path)
    else:
        print("使用默认路径: static/business-headshot-ai/images/options/backdrops")
        rename_type_folders()
