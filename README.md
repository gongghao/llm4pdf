# PDF智能解读系统

基于PPStructure的PDF文档智能解读系统，支持文本提取、图像识别、数学公式识别和智能问答。

## 🚀 主要功能

### 📄 PDF解析
- **PPStructure版面分析**: 使用PaddleOCR的PPStructure模型进行精确的版面分析
- **多元素识别**: 支持文本、图像、表格、数学公式等多种元素识别
- **LaTeX公式提取**: 专门针对数学公式进行识别和提取
- **结构化信息**: 保留文档的原始结构和布局信息

### 🤖 智能问答
- **向量化检索**: 基于TF-IDF和余弦相似度的智能检索
- **上下文提取**: 自动提取相关问题的最相关原文片段
- **多语言支持**: 支持中英文混合问答
- **证据展示**: 提供答案的原文依据

### 🖼️ 图像处理
- **图像提取**: 自动提取PDF中的图像和图表
- **图像描述**: 结合LLM生成图像内容描述
- **图像问答**: 支持基于图像内容的问答

## 🛠️ 技术架构

### 核心组件
- **PPStructure**: PaddleOCR的版面分析工具，用于PDF结构识别
- **PaddleOCR**: 文本识别和图像处理
- **TF-IDF向量化**: 文本相似度计算和检索
- **Streamlit**: Web界面框架
- **LLM API**: 大模型接口（支持Qwen、Doubao、Deepseek等）

### 处理流程
1. **PDF转图像**: 将PDF页面转换为高分辨率图像
2. **版面分析**: 使用PPStructure识别文本、图像、表格、公式等区域
3. **内容提取**: 分别提取各类内容并进行结构化存储
4. **向量化索引**: 构建文本向量索引用于检索
5. **智能问答**: 基于检索结果和LLM生成答案

## 📦 安装说明

### 环境要求
- Python 3.7+
- 8GB+ 内存（推荐16GB）
- 网络连接（用于下载模型）

### 快速安装

1. **克隆项目**
```bash
git clone <repository-url>
cd pdf-intelligent-reader
```

2. **安装依赖**
```bash
# 方法1: 使用安装脚本（推荐）
python install_ppstructure.py

# 方法2: 手动安装
pip install -r requirements.txt
pip install paddleocr[structure]
```

3. **启动应用**
```bash
streamlit run app.py
```

## 🎯 使用指南

### 基本使用
1. 打开浏览器访问 `http://localhost:8501`
2. 在侧边栏上传PDF文件
3. 等待PPStructure完成解析
4. 使用智能问答功能

### 功能说明

#### 📋 文献总结
- 自动生成PDF文档的核心内容总结
- 突出主要创新点和实验结果

#### 🖼️ PDF图片
- 自动提取PDF中的图像和图表
- 支持图像预览和下载

#### 📐 数学公式
- 专门识别和提取LaTeX数学公式
- 按页面组织，支持公式预览

#### 💬 智能问答
- 支持自然语言问答
- 提供示例问题快速开始
- 显示答案和原文依据

### 示例问题
- "本文实验在哪些数据集上完成？"
- "全文的第2张图片描述了什么内容？"
- "总结本文的核心创新点"
- "第3页的公式表达了什么？"

## 🔧 配置说明

### LLM API配置
在 `app.py` 中配置你的API密钥：

```python
# 取消注释并填入你的API密钥
setup_llm_api("deepseek", "your_api_key_here")
```

支持的API类型：
- **Qwen**: 阿里云通义千问
- **Doubao**: 豆包
- **Deepseek**: DeepSeek

### PPStructure配置
在 `ppstructure_utils.py` 中可以调整：

```python
# 检测阈值
args.det_db_thresh = 0.3
args.det_db_box_thresh = 0.5

# 图像分辨率
dpi = 200  # 可调整以提高精度
```

## 📊 性能优化

### 内存优化
- 使用单进程模式避免内存溢出
- 可调整批处理大小
- 支持GPU加速（需要CUDA环境）

### 速度优化
- 模型预加载
- 并行处理多页
- 缓存机制

## 🐛 常见问题

### 模型下载失败
```bash
# 手动下载模型
python -c "from paddleocr import PaddleOCR; PaddleOCR()"
```

### 内存不足
- 降低图像DPI设置
- 使用CPU模式
- 减少批处理大小

### 识别效果不佳
- 提高图像分辨率
- 调整检测阈值
- 检查PDF质量

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 提供PPStructure工具
- [Streamlit](https://streamlit.io/) - Web应用框架
- [scikit-learn](https://scikit-learn.org/) - 机器学习工具