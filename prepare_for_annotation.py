
import os
import sys
import SimpleITK as sitk
import numpy as np
from skimage import transform
from skimage.io import imsave
from tqdm import tqdm
import multiprocessing
from functools import partial

# --- 脚本概述 ---
# 本脚本用于将 3D NIfTI (.nii.gz) 文件批量转换为 2D 图像切片 (PNG)。
# 使用多进程并行处理以提升效率。
# 输出的图像经过特殊处理，以符合 MedSAM 模型的输入要求：
# - 1024x1024 分辨率
# - 3通道 (RGB) 格式
# - PNG 无损压缩
# 这使得输出的切片可以直接用于 MedSAM GUI 进行半自动标注。

# --- 路径配置 ---
# 将项目根目录定义为当前脚本所在位置的上一级目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# 输入目录：存放 .nii.gz 文件的位置
INPUT_NII_DIR = os.path.join(PROJECT_ROOT, 'data', 'nii_data', 'images')

# 输出目录：存放处理后生成的 PNG 切片文件夹
OUTPUT_SLICES_DIR = os.path.join(PROJECT_ROOT, 'data', 'pred_data', 'images')

# MedSAM 要求的图像尺寸
IMAGE_SIZE = 1024

def process_single_nii_file(nii_path, output_dir, image_size):
    """
    处理单个 NIfTI 文件：读取、切片、格式化并保存为 PNG。
    这是一个独立的函数，以便于并行处理。
    """
    try:
        # a. 构建输出文件夹路径
        relative_path = os.path.relpath(nii_path, INPUT_NII_DIR)
        # 移除 .nii.gz 后缀，将文件名本身作为一层目录
        relative_dir = os.path.splitext(os.path.splitext(relative_path)[0])[0]
        slice_output_dir = os.path.join(output_dir, relative_dir)
        os.makedirs(slice_output_dir, exist_ok=True)

        # b. 读取和处理3D影像
        img_sitk = sitk.ReadImage(nii_path)
        image_data = sitk.GetArrayFromImage(img_sitk)

        # c. 影像归一化 (对医疗影像很重要，以获得好的对比度)
        # 使用百分位数去除极端亮点和暗点
        if np.any(image_data):
            lower_bound = np.percentile(image_data[image_data > 0], 0.5)
            upper_bound = np.percentile(image_data[image_data > 0], 99.5)
            image_data_clipped = np.clip(image_data, lower_bound, upper_bound)
            
            # 缩放到 0-255
            image_data_normalized = (
                (image_data_clipped - image_data_clipped.min()) / 
                (image_data_clipped.max() - image_data_clipped.min() + 1e-8) * 255.0
            )
        else:
            image_data_normalized = image_data # 如果是全黑的，则不处理

        image_data_uint8 = np.uint8(image_data_normalized)

        # d. 遍历切片，转换为 MedSAM 格式并保存
        num_slices = image_data_uint8.shape[0]
        for i in range(num_slices):
            slice_2d = image_data_uint8[i, :, :]
            
            # 转换为3通道图像
            img_3c = np.repeat(slice_2d[:, :, None], 3, axis=-1)
            
            # 缩放到 1024x1024
            resized_img = transform.resize(
                img_3c,
                (image_size, image_size),
                order=3,
                preserve_range=True,
                mode='constant',
                anti_aliasing=True,
            )
            
            # 保存为 PNG 文件
            slice_filename = f"slice_{str(i).zfill(3)}.png"
            slice_filepath = os.path.join(slice_output_dir, slice_filename)
            imsave(
                slice_filepath,
                resized_img.astype(np.uint8),
                check_contrast=False
            )
        return f"成功处理: {nii_path}"
    except Exception as e:
        return f"处理文件失败: {nii_path}. 错误: {e}"

def export_nii_to_slices_parallel():
    """
    使用多进程并行遍历输入目录中的所有 .nii.gz 文件，
    将其切片并保存为 MedSAM 兼容的 PNG 格式。
    """
    print("--- 开始将 3D NIfTI 并行转换为 2D 切片 (for MedSAM) ---")

    # 1. 确保输出目录存在
    os.makedirs(OUTPUT_SLICES_DIR, exist_ok=True)
    print(f"输出目录已就绪: {OUTPUT_SLICES_DIR}")

    if not os.path.exists(INPUT_NII_DIR):
        print(f"错误: 输入目录不存在于 '{INPUT_NII_DIR}'。中止操作。")
        return

    # 2. 查找所有 .nii.gz 文件
    nii_files_to_process = []
    for root, dirs, files in os.walk(INPUT_NII_DIR):
        for file in files:
            if file.endswith('.nii.gz'):
                nii_files_to_process.append(os.path.join(root, file))

    if not nii_files_to_process:
        print("在输入目录中没有找到 .nii.gz 文件。")
        return

    print(f"找到 {len(nii_files_to_process)} 个 .nii.gz 文件待处理。")
    
    # 3. 设置并行处理
    num_workers = multiprocessing.cpu_count()
    print(f"将使用 {num_workers} 个核心进行并行处理。")
    
    # 创建一个偏函数，固定 'output_dir' 和 'image_size' 参数
    process_func = partial(process_single_nii_file, output_dir=OUTPUT_SLICES_DIR, image_size=IMAGE_SIZE)

    # 4. 使用进程池执行任务
    with multiprocessing.Pool(processes=num_workers) as pool:
        # 使用 tqdm 显示总体进度
        results = list(tqdm(pool.imap(process_func, nii_files_to_process), total=len(nii_files_to_process), desc="总体处理进度"))

    # 5. 打印处理结果 (可选)
    for res in results:
        if "失败" in res:
            print(res) # 打印错误信息

    print("\n--- 所有 .nii.gz 文件已成功转换为 2D 切片 ---")

if __name__ == "__main__":
    # 在 Windows 和 macOS 上，'spawn' 或 'forkserver' 是更安全的启动方法
    # 尤其是在使用 GUI 库或某些第三方库时
    multiprocessing.set_start_method('spawn', force=True)
    export_nii_to_slices_parallel()
