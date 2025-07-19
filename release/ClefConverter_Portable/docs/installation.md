# 安装指南

本文档将指导您完成谱号转换器的安装过程。

## 系统要求

### 最低要求
- **操作系统**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **内存**: 4GB RAM
- **存储空间**: 2GB 可用空间
- **网络**: 用于下载依赖包

### 推荐配置
- **操作系统**: Windows 11, macOS 12+, Ubuntu 20.04+
- **Python**: 3.9 或更高版本
- **内存**: 8GB RAM 或更多
- **存储空间**: 5GB 可用空间
- **GPU**: 支持CUDA的显卡（可选，用于加速处理）

## 安装步骤

### 1. 安装Python

#### Windows
1. 访问 [Python官网](https://www.python.org/downloads/)
2. 下载Python 3.8+版本
3. 运行安装程序，确保勾选"Add Python to PATH"
4. 验证安装：
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# 使用Homebrew安装
brew install python@3.9

# 或者从官网下载安装包
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.9 python3.9-pip python3.9-venv
```

### 2. 克隆项目

```bash
git clone https://github.com/your-username/clef-converter.git
cd clef-converter
```

### 3. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装基础依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt
```

### 5. 安装项目

```bash
# 开发模式安装
pip install -e .
```

## 可选组件安装

### LilyPond（推荐）

LilyPond用于生成高质量的乐谱图像。

#### Windows
1. 访问 [LilyPond官网](http://lilypond.org/windows.html)
2. 下载并安装最新版本
3. 将LilyPond添加到系统PATH

#### macOS
```bash
brew install lilypond
```

#### Ubuntu/Debian
```bash
sudo apt install lilypond
```

### GPU支持（可选）

如果您有NVIDIA GPU，可以安装CUDA支持以加速处理：

```bash
# 安装PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 安装TensorFlow with GPU
pip install tensorflow[and-cuda]
```

## 验证安装

### 1. 运行测试

```bash
# 运行单元测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_converter.py -v
```

### 2. 命令行测试

```bash
# 显示帮助信息
python main.py --help

# 显示版本信息
python main.py --version
```

### 3. Web界面测试

```bash
# 启动Web服务
python main.py --web

# 在浏览器中访问 http://localhost:5000
```

## 常见问题

### 依赖安装失败

**问题**: pip安装依赖时出错
**解决方案**:
```bash
# 清理pip缓存
pip cache purge

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 逐个安装依赖
pip install opencv-python
pip install pillow
pip install numpy
```

### OpenCV安装问题

**问题**: OpenCV安装失败或运行时错误
**解决方案**:
```bash
# 卸载现有版本
pip uninstall opencv-python opencv-contrib-python

# 重新安装
pip install opencv-python-headless
```

### 内存不足

**问题**: 处理大图片时内存不足
**解决方案**:
1. 增加系统虚拟内存
2. 使用较小的图片进行测试
3. 在代码中启用内存优化选项

### 权限问题

**问题**: 安装时权限不足
**解决方案**:
```bash
# 使用用户安装
pip install --user -r requirements.txt

# 或者使用sudo（Linux/macOS）
sudo pip install -r requirements.txt
```

## 开发环境设置

如果您计划参与开发，请安装额外的开发工具：

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install

# 安装代码格式化工具
pip install black flake8 mypy
```

### 代码质量检查

```bash
# 代码格式化
black src/ tests/

# 代码检查
flake8 src/ tests/

# 类型检查
mypy src/
```

## Docker安装（可选）

如果您偏好使用Docker：

```bash
# 构建镜像
docker build -t clef-converter .

# 运行容器
docker run -p 5000:5000 clef-converter

# 使用docker-compose
docker-compose up
```

## 卸载

如果需要卸载项目：

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境
rm -rf venv

# 删除项目目录
cd ..
rm -rf clef-converter
```

## 更新

更新到最新版本：

```bash
# 拉取最新代码
git pull origin main

# 更新依赖
pip install -r requirements.txt --upgrade

# 重新安装项目
pip install -e .
```

## 技术支持

如果在安装过程中遇到问题：

1. 查看 [故障排除文档](troubleshooting.md)
2. 搜索 [GitHub Issues](https://github.com/your-username/clef-converter/issues)
3. 提交新的Issue描述您的问题
4. 联系开发团队

## 下一步

安装完成后，请阅读：
- [使用说明](usage.md) - 了解如何使用谱号转换器
- [API文档](api.md) - 了解编程接口
- [开发指南](development.md) - 参与项目开发
