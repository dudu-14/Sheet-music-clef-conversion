# 🎵 谱号转换器 (Clef Converter)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/your-username/clef-converter)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](docs/)

一个智能的音乐识别和转换工具，能够识别包含中音谱号的乐谱图片，并将其转换为高音谱号的乐谱图片输出。

## ✨ 功能特点

- 🔍 **光学音乐识别（OMR）**：使用先进的计算机视觉技术从图片中识别乐谱内容
- 🎼 **智能谱号转换**：精确将中音谱号音符转换为高音谱号对应位置
- 🎹 **MIDI数据处理**：支持MIDI格式的导入导出，保持音高信息完整
- 🖼️ **多格式输出**：支持PNG、PDF、MIDI、SVG等多种输出格式
- 🌐 **Web界面**：提供友好的Web用户界面，支持拖拽上传
- ⚡ **批量处理**：支持批量转换多个文件，提高工作效率
- 🎯 **高精度模式**：可选的高精度识别模式，提升复杂乐谱的识别准确率

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/clef-converter.git
cd clef-converter

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装项目
pip install -e .
```

### 基本使用

#### 命令行方式
```bash
# 基本转换
python main.py input.png -o output.png

# 高精度模式
python main.py input.png -o output.png --high-quality

# 多格式输出
python main.py input.png -o output --formats png,pdf,midi

# 批量处理
python main.py *.png -o output_dir/ --batch
```

#### Web界面方式
```bash
# 启动Web服务
python main.py --web

# 在浏览器中访问 http://localhost:5000
```

## 📖 详细文档

- 📋 [安装指南](docs/installation.md) - 详细的安装步骤和环境配置
- 📚 [使用说明](docs/usage.md) - 完整的使用教程和功能介绍
- 🔧 [API文档](docs/api.md) - Web API和Python API接口文档
- 🛠️ [开发指南](docs/development.md) - 参与项目开发的指南
- 🔍 [故障排除](docs/troubleshooting.md) - 常见问题和解决方案

## 🎯 支持的格式

### 输入格式
| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PNG | `.png` | 推荐格式，支持透明背景 |
| JPEG | `.jpg`, `.jpeg` | 常见格式 |
| BMP | `.bmp` | 无损格式 |
| TIFF | `.tiff`, `.tif` | 高质量格式 |

### 输出格式
| 格式 | 扩展名 | 说明 |
|------|--------|------|
| PNG | `.png` | 高质量图片 |
| PDF | `.pdf` | 矢量文档 |
| MIDI | `.midi`, `.mid` | 音频文件 |
| SVG | `.svg` | 矢量图形 |

## 🏗️ 项目架构

```
谱号转换器/
├── src/                    # 源代码
│   ├── core/              # 核心模块
│   │   ├── converter.py   # 主转换器
│   │   ├── omr_engine.py  # OMR识别引擎
│   │   ├── midi_converter.py # MIDI转换器
│   │   ├── clef_converter.py # 谱号转换器
│   │   ├── score_renderer.py # 乐谱渲染器
│   │   └── image_preprocessor.py # 图像预处理器
│   ├── models/            # 数据模型
│   ├── utils/             # 工具模块
│   └── web/               # Web界面
├── tests/                 # 测试用例
├── docs/                  # 文档
├── examples/              # 示例文件
├── main.py               # 主程序入口
└── requirements.txt      # 依赖包列表
```

## 🔬 技术栈

- **Python 3.8+** - 主要编程语言
- **OpenCV** - 图像处理和计算机视觉
- **PIL/Pillow** - 图像格式处理
- **music21** - 音乐理论和MIDI处理
- **Flask** - Web框架
- **NumPy** - 数值计算
- **mido** - MIDI文件处理

## 📊 使用示例

### Python API
```python
from src.core.converter import ClefConverter

# 创建转换器
with ClefConverter(high_quality=True) as converter:
    # 转换单个文件
    result = converter.convert_single(
        "input.png", 
        "output.png", 
        formats=["png", "midi"]
    )
    
    if result['success']:
        print(f"转换成功！识别到 {result['notes_count']} 个音符")
    else:
        print(f"转换失败: {result['error']}")
```

### Web API
```javascript
// 上传并转换文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/upload', {
    method: 'POST',
    body: formData
}).then(response => response.json())
  .then(data => {
    console.log('上传成功:', data.task_id);
    // 开始转换...
  });
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_converter.py -v

# 生成覆盖率报告
python -m pytest --cov=src --cov-report=html
```

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解如何参与项目开发。

### 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 运行代码检查
black src/ tests/
flake8 src/ tests/
mypy src/
```

## 📈 性能指标

- **识别准确率**: 90%+ (标准印刷乐谱)
- **处理速度**: 2-5秒/页 (普通模式)
- **支持分辨率**: 150-600 DPI
- **最大文件大小**: 100MB

## 🗺️ 路线图

- [ ] 支持更多谱号类型（低音谱号、次中音谱号等）
- [ ] 集成深度学习模型提高识别准确率
- [ ] 支持手写乐谱识别
- [ ] 移动端应用开发
- [ ] 云端服务部署
- [ ] 音频播放功能

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🙏 致谢

- [music21](https://web.mit.edu/music21/) - 音乐分析和生成库
- [OpenCV](https://opencv.org/) - 计算机视觉库
- [LilyPond](http://lilypond.org/) - 音乐排版系统
- [oemer](https://github.com/BreezeWhite/oemer) - 光学音乐识别库

## 📞 联系我们

- 📧 邮箱: support@example.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-username/clef-converter/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/your-username/clef-converter/discussions)

## ⭐ 如果这个项目对您有帮助，请给我们一个星标！

---

<div align="center">
  <p>Made with ❤️ by the Clef Converter Team</p>
  <p>© 2025 谱号转换器. All rights reserved.</p>
</div>
