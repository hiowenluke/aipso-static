"""
需求：
1. 遍历 input 目录下的所有文件和子目录。
2. 为每个图片创建同名的子文件夹，并将该图片移动到对应的子文件夹中，改名为"blur-0.webp"
  - 在该子文件夹下，复制 "blur-0.webp" 为 "blur-1.webp"、"blur-2.webp"、"blur-3.webp"。

用法：
python main.py # 使用 "./input"
python main.py ./xxx
"""
import os
import sys
import shutil
from pathlib import Path
from PIL import Image, ImageFilter

def process_images(input_path="input"):
    # 定义输入目录
    input_dir = Path(input_path)
    
    if not input_dir.exists():
        print(f"目录 {input_dir} 不存在！")
        return
    
    # 支持的图片格式
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff'}
    
    # 先收集所有需要处理的图片文件（避免在遍历时修改目录结构）
    images_to_process = []
    for item in input_dir.rglob('*'):
        # 只处理文件，跳过目录
        if not item.is_file():
            continue
            
        # 检查是否是图片文件
        if item.suffix.lower() not in image_extensions:
            continue
        
        # 跳过已经处理过的文件（blur-0.webp, blur-5.webp等）
        if item.stem.startswith('blur-'):
            continue
        
        images_to_process.append(item)
    
    print(f"找到 {len(images_to_process)} 个图片需要处理")
    
    # 处理收集到的图片
    for item in images_to_process:
        # 获取图片所在的目录（可能是 input 或其子目录）
        parent_dir = item.parent
        
        # 获取图片的文件名（不含扩展名）
        image_name = item.stem
        
        # 在图片所在目录下创建同名子文件夹
        target_folder = parent_dir / image_name
        target_folder.mkdir(exist_ok=True)
        
        # 目标文件路径：blur-0.webp
        blur_0_path = target_folder / "blur-0.webp"
        
        # 移动并重命名图片为 blur-0.webp
        shutil.move(str(item), str(blur_0_path))
        print(f"处理: {item} -> {blur_0_path}")
        
        # 创建虚化版本的图片
        # blur_level=1，虚化程度：2
        # blur_level=2，虚化程度：5
        # blur_level=3，虚化程度：10
        blur_mapping = {1: 2, 2: 5, 3: 10}
        
        for blur_level, blur_radius in blur_mapping.items():
            target_file = target_folder / f"blur-{blur_level}.webp"
            
            # 打开原图并应用高斯模糊
            with Image.open(blur_0_path) as img:
                blurred_img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
                blurred_img.save(target_file, 'WEBP', quality=95, method=6)
            
            print(f"  创建虚化图片: {target_file} (虚化程度: {blur_radius})")
            

if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        input_folder = sys.argv[1]
        print(f"使用指定的输入文件夹: {input_folder}")
        process_images(input_folder)
    else:
        print("使用默认输入文件夹: input")
        process_images()
    print("处理完成！")