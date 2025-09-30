# RectSurgNet_3D_Segment

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![GitHub Stars](https://img.shields.io/github/stars/Miyamoto98/RectSurgNet_3D_Segment?style=social)](https://github.com/Miyamoto98/RectSurgNet_3D_Segment/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/Miyamoto98/RectSurgNet_3D_Segment?style=social)](https://github.com/Miyamoto98/RectSurgNet_3D_Segment/network/members)

## 简介 (Introduction)

`RectSurgNet_3D_Segment` 是一个专注于 3D 医疗影像（如 MRI/CT）的半自动分割与标注项目。它提供了一套完整的工具链，旨在赋能医疗专家，通过高效的预处理流程、基于 MedSAM2 的模型推理以及交互式标注工具，快速、准确地对三维影像数据进行区域识别、分割和高质量标注，为后续的模型训练和分析提供数据基础。

**主要工作流程：**

1.  **数据预处理：** 将原始 DICOM 影像转换为 NIfTI 格式，再进一步转换为 2D PNG 切片，以适应标注工具和模型推理的输入要求。
2.  **模型推理：** 利用 MedSAM2 模型对 3D 影像进行自动或半自动分割预测。
3.  **交互式标注：** 使用功能丰富的 GUI 工具对 2D 影像切片进行半自动标注，生成高质量的分割 mask。
4.  **数据输出：** 标注结果和模型预测结果将以 mask 文件或 NIfTI 格式保存，可直接用于后续的模型训练。

## 特性 (Features)

*   **3D 医疗影像处理**: 支持处理 DICOM 原始数据，并转换为 NIfTI (.nii.gz) 格式。
*   **高效数据准备工具**: 包含 `prepare_dataset.py` 用于 DICOM 到 NIfTI 的转换和数据结构组织，以及 `prepare_for_annotation.py` 用于 NIfTI 到 MedSAM 兼容 2D PNG 切片的转换。
*   **集成 MedSAM2 模型**: 利用 MedSAM2 模型进行高效的医学图像分割，支持 RECIST 病灶的 3D 传播推理。
*   **交互式 GUI 标注工具**: 提供直观的图形用户界面 (`MedSAM2/GUI.py`)，支持点、框提示和手动绘制/擦除等多种标注模式。
*   **模型检查点**: 包含预训练的 MedSAM2 模型检查点，方便快速部署和实验。
*   **多进程并行处理**: 数据预处理脚本支持多进程，提升处理效率。

## 先决条件 (Prerequisites)

在开始之前，请确保您的系统满足以下要求：

*   **操作系统：** Windows 10/11 (或其他兼容 Python 和 Tkinter 的系统)
*   **Python 环境：** 建议使用 Python 3.8 或更高版本。
*   **GPU (推荐)：** 为了加速模型推理，建议使用 NVIDIA GPU 并安装相应的 CUDA 驱动。
*   **依赖库：** 您需要安装项目所需的 Python 库。

## 环境设置 (Environment Setup)

**重要提示：** 在以下所有命令行示例中，`[您的项目根目录]` 代表您本地 `RectSurgNet_3D_Segment` 项目的绝对路径。请在执行命令时将其替换为实际路径。

1.  **克隆仓库**: 
    ```bash
    git clone https://github.com/Miyamoto98/RectSurgNet_3D_Segment.git
    cd RectSurgNet_3D_Segment
    ```

2.  **创建并激活虚拟环境 (推荐)**:
    打开您的命令提示符 (CMD) 或 PowerShell，导航到项目根目录，然后执行以下命令：
    ```cmd
    cd [您的项目根目录]
    python -m venv venv
    # Windows
    .Venv\Scripts\activate
    # macOS/Linux (如果适用)
    source venv/bin/activate
    ```

3.  **安装依赖**: 
    在激活的虚拟环境中，执行以下命令安装所有必需的库：
    ```bash
    pip install -r requirements.txt
    ```
    *注意：* 如果安装 `torch` 遇到问题，请参考 PyTorch 官方网站 (https://pytorch.org/get-started/locally/) 获取适合您系统和 CUDA 版本的安装命令。

## 数据准备流程 (Data Preparation Flow)

本节将指导您如何将原始医疗影像数据转换为标注工具和模型推理可用的格式。

### 1. 放置原始数据

将您需要处理的原始 DICOM 影像数据（通常是包含多个 `.dcm` 文件的文件夹）放置到以下目录结构中：

`[您的项目根目录]\data\raw_mri_data\`

例如，如果您有患者“张三”的“治疗前”和“治疗后”的 DICOM 序列，它们应该放在：
`[您的项目根目录]\data\raw_mri_data\张三\治疗前\SE001\`
`[您的项目根目录]\data\raw_mri_data\张三\治疗后\SE002\`
...以此类推。

### 2. 转换为 NIfTI 格式

运行 `prepare_dataset.py` 脚本将 DICOM 序列转换为 NIfTI (.nii.gz) 格式。

1.  **打开命令行/PowerShell**，导航到项目根目录并激活虚拟环境。
2.  **运行脚本：**
    ```cmd
    python prepare_dataset.py
    ```
    *   **功能：** 该脚本会遍历 `data/raw_mri_data` 中的所有 DICOM 序列，将其转换为 `.nii.gz` 文件。
    *   **输出：** 转换后的 NIfTI 文件将保存到 `[您的项目根目录]\data\nii_data\images\` 目录中。文件名将包含原始的患者和治疗阶段信息，例如 `张三_治疗前_SE001.nii.gz`。

### 3. 转换为 2D PNG 切片

运行 `prepare_for_annotation.py` 脚本将 NIfTI 文件转换为 2D PNG 图像切片，这些切片是 GUI 标注工具的直接输入。

1.  **打开命令行/PowerShell**，导航到项目根目录并激活虚拟环境。
2.  **运行脚本：**
    ```cmd
    python prepare_for_annotation.py
    ```
    *   **功能：** 该脚本会读取 `data/nii_data/images` 中的 NIfTI 文件，将其切片并处理成 1024x1024 像素、3 通道 (RGB) 的 PNG 图像。
    *   **输出：** 生成的 2D PNG 切片将保存到 `[您的项目根目录]\data\pred_data\images\` 目录中。每个 NIfTI 文件会对应一个子文件夹，其中包含所有切片，例如 `data\pred_data\images\张三_治疗前_SE001\slice_000.png`。

## 模型推理 (Model Inference)

本项目集成了 MedSAM2 模型，用于 3D 医疗影像的自动或半自动分割。`MedSAM2/medsam2_infer_CT_lesion_npz_recist.py` 脚本负责执行此功能。

### 运行推理脚本

1.  **打开命令行/PowerShell**，导航到项目根目录并激活虚拟环境。
2.  **运行脚本：**
    ```cmd
    python MedSAM2/medsam2_infer_CT_lesion_npz_recist.py --checkpoint medsam2_recist --imgs_path ./data/validation_public_npz --pred_save_dir ./data/RECIST_pred --sample_points from_recist_n
    ```
    *   **功能：** 该脚本使用预训练的 MedSAM2 模型对输入的 NPZ 格式影像数据进行 3D 病灶分割。它支持通过边界框或提示点进行传播，并可选择保存 NIfTI 格式的分割结果和叠加图像。
    *   **参数说明：**
        *   `--checkpoint`: 指定使用的模型检查点，例如 `medsam2_recist`。
        *   `--imgs_path`: 输入影像 NPZ 文件的路径。
        *   `--pred_save_dir`: 预测结果的保存目录。
        *   `--sample_points`: 提示点采样策略 (`from_box`, `from_recist_n`, `from_recist_center`, `from_recist_3`)。
        *   `--propagate_with_box`: (可选) 使用边界框进行传播。
        *   `--save_nifti`: (可选) 保存 NIfTI 格式的分割结果。
        *   `--save_overlay`: (可选) 保存带有分割结果叠加的 PNG 图像。
    *   **输出：** 分割结果将保存为 NPZ 文件，如果指定，还会生成 NIfTI 格式的分割文件和叠加图像。

## 交互式标注 (Interactive Annotation)

完成数据预处理后，您可以启动标注工具对 2D 影像切片进行标注。

### 1. 启动标注工具

1.  **打开命令行/PowerShell**，导航到项目根目录并激活虚拟环境。
2.  **运行 GUI：**
    ```cmd
    python MedSAM2/GUI.py
    ```
    这将启动标注界面，并自动加载 `data/pred_data/images/` 目录中的影像进行处理。

### 2. GUI 操作指南

GUI 界面设计直观，提供多种交互模式和导航功能，以提高标注效率。

*   **状态显示：** 界面顶部会显示当前正在处理的文件路径（包含父目录）和进度（例如：`Processing: 患者ID_序列ID\slice_000.png (1/100)`）。

*   **文件导航：**
    *   **`< Prev` / `Next >`：** 逐个切换到上一张或下一张图像切片。
    *   **`< Prev Folder`：** 跳转到上一个文件夹的第一张图像。
    *   **`Skip Folder >`：** 跳过当前文件夹中所有剩余图像，直接跳转到下一个文件夹的第一张图像。

*   **标注模式：**
    *   **`Prompt Mode` (默认)：**
        *   **左键点击：** 添加正向提示点（绿色），引导模型分割。
        *   **右键点击：** 添加负向提示点（红色），告诉模型不要分割该区域。
        *   **中键拖动：** 绘制一个边界框（蓝色），模型将尝试在该区域内进行分割。
        *   每次添加点或框后，模型会自动进行分割预测。
    *   **`Manual Pen (Red Draw)`：** 切换到手动画笔模式。您可以用鼠标左键在图像上直接绘制红色区域，用于精细修正分割结果。
    *   **`Manual Eraser`：** 切换到手动橡皮擦模式。您可以用鼠标左键擦除图像上不需要的分割区域或手动绘制的痕迹。

*   **画笔/橡皮擦大小：** 通过滑动条调整画笔或橡皮擦的大小。

*   **操作按钮：**
    *   **`Save Mask (Ctrl+S)`：** 保存当前图像的分割 mask。 mask 将保存到 `[您的项目根目录]\data\pred_data\labels\` 目录中，并保持与原始图像相同的相对路径和文件名（例如：`患者ID_序列ID\slice_000_mask.png`）。保存后会自动加载下一张图像。
    *   **`DELETE & Skip File`：** 从处理列表中移除当前文件，并尝试从磁盘上删除该文件。然后加载下一张图像。**请谨慎使用此功能。**
    *   **`Clear Prompts/Mask`：** 清除当前图像上的所有提示点、边界框和生成的 mask，恢复到原始图像状态。
    *   **`Undo (Ctrl+Z)`：** 撤销上一步操作。
    *   **`Redo (Ctrl+Y)`：** 重做上一步被撤销的操作。

## 输出结果 (Output Results)

所有标注完成的分割 mask 将保存到以下目录：

`[您的项目根目录]\data\pred_data\labels\`

Mask 文件将以 PNG 格式存储，文件名格式为 `[原始文件名]_mask.png`，并保留原始图像的文件夹结构。

模型推理的输出结果（NPZ、NIfTI 或叠加图像）将根据您在运行推理脚本时指定的 `--pred_save_dir` 参数保存。

## 寻求帮助 (Seeking Help)

如果您在使用过程中遇到任何问题，或有改进建议，请通过 GitHub Issues 联系项目维护人员。

## 版权 (Copyright)

Copyright &copy; 2025 Miyamoto98. 保留所有权利。

## 许可证 (License)

本项目使用 MIT 许可证。详情请参阅 `LICENSE` 文件。
