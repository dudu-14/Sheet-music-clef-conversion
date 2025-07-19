# 发布文件目录

本目录包含谱号转换器的发布版本和构建工具。

## 目录结构

```
release/
├── README.md              # 本文件
├── release_files/         # 构建工具和资源文件
│   ├── build_exe.py      # PyInstaller打包脚本
│   ├── create_icon.py    # 图标生成脚本
│   ├── icon.ico          # Windows图标文件
│   └── icon.png          # PNG图标文件
└── 1.0.0/                # v1.0.0版本发布文件
    ├── ClefConverter.exe # Windows可执行文件
    ├── ClefConverter_Portable/ # 便携版包
    └── README.md         # 版本说明
```

## 版本说明

### v1.0.0 (2025-01-XX)
- 🎵 完整的中音谱号到高音谱号转换功能
- 🔍 光学音乐识别（OMR）引擎
- 🎹 MIDI文件处理和转换
- 🖼️ 多格式输出支持（PNG, PDF, MIDI, SVG）
- 🌐 现代化Web用户界面
- ⚡ 批量处理功能

## 使用说明

### Windows用户
1. 下载对应版本目录中的 `ClefConverter.exe`
2. 双击运行，或在命令行中使用

### 便携版
1. 下载 `ClefConverter_Portable` 文件夹
2. 运行 `start.bat` 启动Web界面
3. 或使用 `convert.bat` 进行命令行转换

## 构建说明

如果需要重新构建可执行文件：

1. 进入 `release_files` 目录
2. 运行 `python build_exe.py`
3. 构建完成的文件将输出到对应版本目录

## 系统要求

- **Windows**: Windows 10/11 (64位)
- **内存**: 最少4GB RAM，推荐8GB
- **存储**: 至少500MB可用空间
- **网络**: 用于Web界面访问（可选）

## 许可证

本软件采用 MIT 许可证，详见项目根目录的 LICENSE 文件。
