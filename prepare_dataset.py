
import os
import sys
from tqdm import tqdm

# --- 脚本概述 ---
# 本脚本为准备 NIfTI 数据集的一站式解决方案。
#
# 合并功能:
# 1. 处理 'raw_mri_data' 中的所有 DICOM 序列。
# 2. 将它们转换为 .nii.gz 格式。
# 3. 保存到 'nii_data/images' 目录，并保持原始的子目录结构。
# 4. 创建一个空的 'nii_data/labels' 目录供将来使用。
#
# 本脚本替代并合并了 'process_all_dicom.py' 和 'reorganize_nii_structure.py' 的功能。

# --- 路径配置 ---
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'raw_mri_data')
NII_DATA_DIR = os.path.join(PROJECT_ROOT, 'segment', 'nii_data')
NII_IMAGES_DIR = os.path.join(NII_DATA_DIR, 'images')
NII_LABELS_DIR = os.path.join(NII_DATA_DIR, 'labels') # 为 labels 文件夹创建路径

# 将项目根目录添加到 Python 路径中，以便导入 'utils' 包
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from utils.format_convert import dcm2nii
except ImportError as e:
    print(f"错误: 无法从 'utils.format_convert' 导入 dcm2nii 函数。")
    print(f"请确保 'utils' 目录及其文件存在。")
    print(f"Import Error: {e}")
    sys.exit(1)

def prepare_nifti_dataset():
    """
    遍历原始数据，转换 DICOM 为 NIfTI 并组织输出结构。
    """
    print("--- 开始完整的数据集准备流程 ---")

    # 1. 创建主要的目标文件夹 ('images' 和 'labels')
    print("步骤 1: 创建目标文件夹...")
    os.makedirs(NII_IMAGES_DIR, exist_ok=True)
    os.makedirs(NII_LABELS_DIR, exist_ok=True)
    print(f"  - Images 目录已就绪: {NII_IMAGES_DIR}")
    print(f"  - Labels 目录已就绪: {NII_LABELS_DIR}")

    if not os.path.exists(RAW_DATA_DIR):
        print(f"错误: 原始数据目录 '{RAW_DATA_DIR}' 不存在。中止操作。")
        return

    # 2. 查找所有 DICOM 序列文件夹
    print("\n步骤 2: 在 'raw_mri_data' 中扫描 DICOM 序列...")
    dicom_series_paths = []
    for root, dirs, files in os.walk(RAW_DATA_DIR):
        if os.path.basename(root).startswith('SE'):
            dicom_series_paths.append(root)

    if not dicom_series_paths:
        print("没有找到需要处理的 'SE' 文件夹。无需转换。" )
        print("\n--- 准备流程结束 ---")
        return

    print(f"找到 {len(dicom_series_paths)} 个 DICOM 序列待转换。")

    # 3. 处理找到的每一个序列
    print("\n步骤 3: 将 DICOM 序列转换为 NIfTI 格式...")
    for dcm_path in tqdm(dicom_series_paths, desc="转换进度"):
        try:
            relative_path = os.path.relpath(dcm_path, RAW_DATA_DIR)
            output_filename = f"{os.path.basename(dcm_path)}.nii.gz"
            output_dir = os.path.join(NII_IMAGES_DIR, os.path.dirname(relative_path))
            output_nii_path = os.path.join(output_dir, output_filename)

            if os.path.exists(output_nii_path):
                continue

            os.makedirs(output_dir, exist_ok=True)
            dcm2nii(dcm_path, output_nii_path)

        except Exception as e:
            print(f"  - 处理失败 {dcm_path}. 错误: {e}")

    print("\n--- 完整数据集准备流程结束 ---")

if __name__ == "__main__":
    prepare_nifti_dataset()
