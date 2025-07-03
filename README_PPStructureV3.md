# PPStructureV3 PDF解析模块

## 概述

这是一个基于PaddleOCR PPStructureV3的PDF文档解析模块，整合了`parser.py`中的图片补充功能和`test.py`中的PPStructureV3使用方式。该模块提供了完整的PDF文档结构分析、文本提取、图片识别、表格检测和公式提取功能。

## 主要特性

### 🔧 核心功能
- **结构化解析**: 使用PPStructureV3进行智能版面分析
- **图片补充**: 结合PDF原生图片信息和AI检测结果
- **多格式输出**: 支持Markdown、图片、JSON等多种输出格式
- **完整分析**: 提供文本、图片、表格、公式的全面提取

### 📊 支持的元素类型
- **文本**: 标题、正文、列表等
- **图片**: 图表、照片、插图等
- **表格**: 数据表格、统计表等
- **公式**: 数学公式、化学式等

## 安装依赖

```bash
pip install paddleocr
pip install PyMuPDF
pip install Pillow
pip install opencv-python
pip install numpy
```

## 快速开始

### 基础使用

```python
from ppstructure_utils import extract_pdf_structure, get_detailed_analysis

# 基础结构提取
result = extract_pdf_structure("document.pdf", "./output")
if result["success"]:
    print(f"提取了 {result['page_count']} 页")
    print(f"Markdown文件: {result['markdown_file']}")

# 详细分析
analysis = get_detailed_analysis("document.pdf", "./output")
if analysis["success"]:
    stats = analysis["statistics"]
    print(f"总页数: {stats['total_pages']}")
    print(f"总图片数: {stats['total_images']}")
    print(f"总表格数: {stats['total_tables']}")
    print(f"总公式数: {stats['total_formulas']}")
```

### 高级使用

```python
from ppstructure_utils import PPStructureV3Extractor

# 创建自定义提取器
extractor = PPStructureV3Extractor(
    table=True,      # 启用表格识别
    ocr=True,        # 启用OCR
    show_log=False   # 关闭日志
)

# 提取特定内容
text = extractor.extract_text_only("document.pdf")
images = extractor.extract_images_with_layout("document.pdf", "./pics")
tables = extractor.extract_tables("document.pdf")
formulas = extractor.extract_formulas("document.pdf")
```

## API参考

### 主要函数

#### `extract_pdf_structure(pdf_path, output_dir="./output")`
提取PDF的完整结构信息。

**参数:**
- `pdf_path`: PDF文件路径
- `output_dir`: 输出目录

**返回:**
```python
{
    "markdown_text": "完整的markdown文本",
    "markdown_file": "markdown文件路径",
    "images": [图片信息列表],
    "page_count": 页数,
    "success": True/False
}
```

#### `get_detailed_analysis(pdf_path, output_dir="./output")`
获取PDF的详细分析结果。

**返回:**
```python
{
    "structure": 结构信息,
    "images": 图片列表,
    "tables": 表格列表,
    "formulas": 公式列表,
    "statistics": {
        "total_pages": 总页数,
        "total_images": 总图片数,
        "total_tables": 总表格数,
        "total_formulas": 总公式数,
        "text_length": 文本长度
    },
    "success": True/False
}
```

### 类方法

#### `PPStructureV3Extractor`

**初始化参数:**
- `table`: 是否启用表格识别 (默认: True)
- `ocr`: 是否启用OCR (默认: True)
- `show_log`: 是否显示日志 (默认: False)

**主要方法:**
- `extract_pdf_structure()`: 提取PDF结构
- `extract_text_only()`: 仅提取文本
- `extract_images_with_layout()`: 提取图片（含布局分析）
- `extract_tables()`: 提取表格
- `extract_formulas()`: 提取公式
- `get_detailed_analysis()`: 详细分析

## 图片补充机制

### 工作原理

该模块实现了类似`parser.py`中的图片补充功能：

1. **PPStructureV3检测**: 使用AI模型检测页面中的图片
2. **PDF原生信息**: 从PDF文件结构中提取图片信息
3. **智能补充**: 将AI遗漏的图片补充到结果中
4. **坐标转换**: 处理PDF坐标与图像坐标的转换

### 补充逻辑

```python
def supplement_missing_figures(layout, images):
    """补充缺失的图片"""
    initial_figure_count = count_initial_figures(layout)
    for image_info in images[initial_figure_count:]:
        # 坐标转换和插入逻辑
        bbox = tuple(int(x) * 2 for x in image_info["bbox"])
        number = image_info["number"] - 1
        # 插入到正确位置并重新排序
```

## 输出结构

### 目录结构
```
output/
├── document.md          # Markdown文件
├── images/              # 图片目录
│   ├── page1_img1.png
│   └── page2_img1.png
└── analysis.json        # 分析结果（可选）

pics/                    # 图片提取目录
├── page1_ppstructure_1.png
└── page2_ppstructure_1.png
```

### 图片信息格式
```python
{
    "page": 1,                    # 页码
    "path": "完整路径",           # 图片保存路径
    "relative_path": "相对路径",  # 相对路径
    "size": (width, height),      # 图片尺寸
    "source": "ppstructure",      # 来源（ppstructure/pdf_native）
    "bbox": [x1, y1, x2, y2]     # 边界框（如果可用）
}
```

## 测试

运行测试脚本：

```bash
python test_ppstructure.py
```

测试内容包括：
- 基础PDF提取功能
- 详细分析功能
- 各个独立功能测试
- 自定义提取器测试

## 性能优化

### 内存优化
- 使用单进程模式避免内存泄漏
- 及时释放大型对象
- 分批处理大文件

### 速度优化
- 智能缩放：大图像自动降采样
- 并行处理：支持多页并行分析
- 缓存机制：避免重复计算

## 错误处理

模块包含完善的错误处理机制：

```python
try:
    result = extract_pdf_structure("document.pdf")
    if result["success"]:
        # 处理成功结果
        pass
    else:
        # 处理错误
        print(f"错误: {result.get('error')}")
except Exception as e:
    print(f"异常: {e}")
```

## 兼容性

- **Python版本**: 3.7+
- **操作系统**: Windows, Linux, macOS
- **PDF格式**: 支持标准PDF文件
- **图像格式**: PNG, JPEG, BMP等

## 注意事项

1. **首次运行**: 会自动下载模型文件，需要网络连接
2. **内存使用**: 处理大文件时注意内存使用情况
3. **输出目录**: 确保有足够的磁盘空间
4. **文件权限**: 确保对输出目录有写权限

## 更新日志

### v2.0.0 (重构版本)
- 升级到PPStructureV3
- 整合图片补充功能
- 优化API设计
- 增强错误处理
- 添加详细分析功能

### v1.0.0 (原始版本)
- 基础PDF解析功能
- PPStructureV2支持
- 简单的文本和图片提取

## 贡献

欢迎提交Issue和Pull Request来改进这个模块。

## 许可证

MIT License 