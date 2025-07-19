# 🎵 谱号转换器 v1.0.0 发布说明

## 🎉 首个正式版本发布！

谱号转换器 v1.0.0 是一个智能的音乐识别和转换工具，能够识别包含中音谱号的乐谱图片，并将其转换为高音谱号的乐谱输出。

## ✨ 主要功能

### 🔍 光学音乐识别 (OMR)
- 智能图像预处理和增强
- 自动谱号检测和识别
- 精确的音符位置识别
- 五线谱结构分析

### 🎼 谱号转换
- 中音谱号到高音谱号的精确转换
- 保持原始音高不变
- 自动处理加线音符
- 智能布局优化

### 🎹 MIDI处理
- 生成标准MIDI文件
- 保持节拍和时值信息
- 支持多轨道输出
- 音符时间量化

### 🖼️ 多格式输出
- **PNG** - 高质量图片格式
- **PDF** - 矢量文档格式
- **MIDI** - 标准音频格式
- **SVG** - 可缩放矢量图形

### 🌐 用户界面
- 现代化响应式Web界面
- 拖拽文件上传支持
- 实时进度显示
- 批量文件处理

## 📦 发布文件

### ClefConverter.exe (59MB)
- **类型**: Windows 64位可执行文件
- **依赖**: 无需安装Python或其他依赖
- **功能**: 完整的转换功能

### ClefConverter_Portable/ 
便携版包，包含：
- `ClefConverter.exe` - 主程序
- `start_web.bat` - 一键启动Web界面
- 完整的独立运行环境

## 🚀 使用方法

### 方法1: Web界面 (推荐)
```bash
# 下载并运行
ClefConverter.exe --web

# 或使用便携版
双击 start_web.bat
```
然后在浏览器中访问 http://localhost:5000

### 方法2: 命令行
```bash
# 基本转换
ClefConverter.exe input.png -o output.png

# 高精度模式
ClefConverter.exe input.png -o output.png --high-quality

# 多格式输出
ClefConverter.exe input.png -o output --formats png,pdf,midi

# 批量处理
ClefConverter.exe *.png -o output_dir/ --batch

# 查看帮助
ClefConverter.exe --help
```

## 💻 系统要求

### 最低要求
- **操作系统**: Windows 10 (64位)
- **内存**: 4GB RAM
- **存储**: 500MB 可用空间
- **输入格式**: PNG, JPG, BMP, TIFF

### 推荐配置
- **操作系统**: Windows 11 (64位)
- **内存**: 8GB RAM 或更多
- **存储**: 2GB 可用空间
- **硬盘**: SSD (提升处理速度)

## 📊 性能指标

- **识别准确率**: 90%+ (标准印刷乐谱)
- **处理速度**: 2-5秒/页 (普通模式)
- **支持分辨率**: 150-600 DPI
- **最大文件大小**: 100MB

## 🔧 技术特性

- **模块化架构**: 清晰的分层设计
- **错误处理**: 完善的异常处理机制
- **进度跟踪**: 实时处理进度显示
- **内存优化**: 高效的内存管理
- **批量处理**: 支持大规模文件处理

## 📚 文档和支持

- **完整文档**: 项目包含详细的使用说明和API文档
- **示例文件**: 提供测试用的示例乐谱
- **故障排除**: 详细的问题解决指南

## 🐛 已知问题

- 手写乐谱识别准确率相对较低
- 复杂多声部乐谱可能需要手动调整
- 非标准字体可能影响识别效果

## 🔄 更新计划

- 支持更多谱号类型 (低音谱号、次中音谱号)
- 集成深度学习模型提高识别准确率
- 支持手写乐谱识别
- 移动端应用开发

## 📞 技术支持

- **GitHub**: https://github.com/dudu-14/Sheet-music-clef-conversion
- **Issues**: 问题反馈和功能建议
- **Discussions**: 技术讨论和使用交流

## 📄 许可证

本项目采用 MIT 许可证，允许自由使用、修改和分发。

## 🙏 致谢

感谢所有为项目做出贡献的开发者和用户！

---

**下载地址**: [GitHub Releases](https://github.com/dudu-14/Sheet-music-clef-conversion/releases/tag/v1.0.0)

**项目主页**: https://github.com/dudu-14/Sheet-music-clef-conversion

© 2025 谱号转换器团队. 保留所有权利.
