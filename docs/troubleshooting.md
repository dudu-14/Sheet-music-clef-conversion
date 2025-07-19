# 故障排除

本文档帮助您解决使用谱号转换器时可能遇到的常见问题。

## 安装问题

### Python版本不兼容

**问题**: 提示Python版本过低
```
ERROR: Python 3.7 is not supported
```

**解决方案**:
1. 检查Python版本：`python --version`
2. 升级到Python 3.8+
3. 使用虚拟环境隔离版本

### 依赖包安装失败

**问题**: pip安装依赖时出错
```
ERROR: Failed building wheel for opencv-python
```

**解决方案**:
```bash
# 方案1：升级pip和setuptools
pip install --upgrade pip setuptools wheel

# 方案2：使用预编译包
pip install opencv-python-headless

# 方案3：使用conda
conda install opencv

# 方案4：逐个安装依赖
pip install numpy
pip install pillow
pip install opencv-python
```

### 权限错误

**问题**: 安装时权限不足
```
ERROR: Permission denied
```

**解决方案**:
```bash
# 使用用户安装
pip install --user -r requirements.txt

# 或者使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## 运行时问题

### 模块导入错误

**问题**: 找不到模块
```
ModuleNotFoundError: No module named 'src'
```

**解决方案**:
1. 确保在项目根目录运行
2. 检查PYTHONPATH设置
3. 使用开发模式安装：`pip install -e .`

### 内存不足

**问题**: 处理大文件时内存溢出
```
MemoryError: Unable to allocate array
```

**解决方案**:
1. 减小图片尺寸
2. 增加系统虚拟内存
3. 分块处理大图片
4. 关闭其他程序释放内存

### 文件权限问题

**问题**: 无法读取或写入文件
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
1. 检查文件权限
2. 以管理员身份运行
3. 更改文件所有者
4. 使用不同的输出目录

## 识别问题

### 识别准确率低

**问题**: 音符识别错误或遗漏

**可能原因**:
- 图片质量差
- 分辨率过低
- 手写乐谱
- 非标准字体

**解决方案**:
1. 提高图片质量
   ```bash
   # 启用高精度模式
   python main.py input.png -o output.png --high-quality
   ```

2. 图片预处理
   - 调整对比度和亮度
   - 去除噪点和污渍
   - 确保图像清晰

3. 分段处理
   - 将复杂乐谱分成小段
   - 单独处理每个系统

### 谱号识别错误

**问题**: 无法正确识别中音谱号

**解决方案**:
1. 确认图片包含完整的中音谱号
2. 检查谱号是否清晰可见
3. 手动裁剪谱号区域
4. 使用标准印刷乐谱

### 音符位置错误

**问题**: 转换后音符位置不正确

**解决方案**:
1. 检查原始识别结果
2. 验证五线谱线条检测
3. 手动校正MIDI文件
4. 重新扫描原始乐谱

## 转换问题

### 输出文件为空

**问题**: 生成的文件没有内容

**可能原因**:
- 没有识别到音符
- 转换过程出错
- 文件写入失败

**解决方案**:
1. 检查日志输出
   ```bash
   python main.py input.png -o output.png --verbose
   ```

2. 验证输入文件
3. 检查输出目录权限
4. 尝试不同的输出格式

### MIDI文件无法播放

**问题**: 生成的MIDI文件损坏

**解决方案**:
1. 使用MIDI验证工具检查
2. 尝试不同的MIDI播放器
3. 检查音符时间信息
4. 重新生成MIDI文件

### PDF渲染失败

**问题**: 无法生成PDF文件

**可能原因**:
- LilyPond未安装
- 字体缺失
- 内存不足

**解决方案**:
1. 安装LilyPond
   ```bash
   # Ubuntu
   sudo apt install lilypond
   
   # macOS
   brew install lilypond
   
   # Windows: 从官网下载安装
   ```

2. 检查字体安装
3. 降低输出质量

## Web界面问题

### 无法访问Web界面

**问题**: 浏览器无法打开页面

**解决方案**:
1. 检查服务是否启动
   ```bash
   python main.py --web --verbose
   ```

2. 确认端口未被占用
   ```bash
   # 使用不同端口
   python main.py --web --port 8080
   ```

3. 检查防火墙设置
4. 尝试不同的浏览器

### 文件上传失败

**问题**: 无法上传图片文件

**可能原因**:
- 文件格式不支持
- 文件过大
- 网络连接问题

**解决方案**:
1. 检查文件格式（支持PNG, JPG, BMP, TIFF）
2. 压缩文件大小（最大100MB）
3. 检查网络连接
4. 清除浏览器缓存

### 处理进度卡住

**问题**: 进度条长时间不更新

**解决方案**:
1. 刷新页面
2. 检查服务器日志
3. 重新上传文件
4. 重启Web服务

## 性能问题

### 处理速度慢

**问题**: 转换时间过长

**优化方案**:
1. 关闭高精度模式
2. 减小图片尺寸
3. 使用SSD硬盘
4. 增加系统内存
5. 启用GPU加速（如果支持）

### 内存使用过高

**问题**: 系统内存占用过多

**解决方案**:
1. 处理较小的图片
2. 分批处理文件
3. 定期重启服务
4. 监控内存使用

## 日志和调试

### 启用详细日志

```bash
# 命令行详细输出
python main.py input.png -o output.png --verbose

# Web服务调试模式
python main.py --web --verbose
```

### 查看日志文件

```bash
# 查看应用日志
tail -f logs/clef_converter.log

# 查看错误日志
grep ERROR logs/clef_converter.log
```

### 调试模式

```python
# Python代码调试
import logging
logging.basicConfig(level=logging.DEBUG)

from src.core.converter import ClefConverter
converter = ClefConverter(verbose=True)
```

## 常见错误代码

| 错误代码 | 说明 | 解决方案 |
|----------|------|----------|
| E001 | 文件不存在 | 检查文件路径 |
| E002 | 格式不支持 | 使用支持的图片格式 |
| E003 | 文件损坏 | 重新扫描或获取文件 |
| E004 | 内存不足 | 增加内存或减小文件 |
| E005 | 权限不足 | 检查文件权限 |
| E006 | 网络错误 | 检查网络连接 |
| E007 | 服务超时 | 重试或联系支持 |

## 获取帮助

如果以上解决方案都无法解决您的问题：

1. **查看文档**
   - [安装指南](installation.md)
   - [使用说明](usage.md)
   - [API文档](api.md)

2. **搜索已知问题**
   - GitHub Issues
   - 常见问题FAQ

3. **提交问题报告**
   - 描述问题现象
   - 提供错误日志
   - 说明系统环境
   - 附上示例文件

4. **联系技术支持**
   - 邮箱：support@example.com
   - GitHub：提交Issue
   - 论坛：技术讨论区
