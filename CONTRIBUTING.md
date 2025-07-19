# 贡献指南

感谢您对谱号转换器项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能

## 开始之前

在开始贡献之前，请：

1. 阅读我们的 [行为准则](#行为准则)
2. 查看 [开发指南](docs/development.md)
3. 搜索现有的 [Issues](https://github.com/your-username/clef-converter/issues) 避免重复

## 如何贡献

### 报告Bug

如果您发现了Bug，请：

1. 确保Bug尚未被报告
2. 创建一个新的Issue
3. 使用Bug报告模板
4. 提供详细的重现步骤
5. 包含系统环境信息

### 提出功能建议

如果您有新功能的想法：

1. 检查是否已有类似建议
2. 创建一个Feature Request Issue
3. 详细描述功能需求和使用场景
4. 说明为什么这个功能有价值

### 提交代码

#### 开发环境设置

```bash
# 1. Fork项目到您的GitHub账户

# 2. 克隆您的Fork
git clone https://github.com/your-username/clef-converter.git
cd clef-converter

# 3. 添加上游仓库
git remote add upstream https://github.com/original-owner/clef-converter.git

# 4. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 5. 安装开发依赖
pip install -r requirements-dev.txt
pip install -e .

# 6. 安装pre-commit钩子
pre-commit install
```

#### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **编写代码**
   - 遵循项目的代码规范
   - 添加必要的测试
   - 更新相关文档

3. **运行测试**
   ```bash
   # 运行所有测试
   pytest

   # 运行代码检查
   black src/ tests/
   flake8 src/ tests/
   mypy src/

   # 检查测试覆盖率
   pytest --cov=src --cov-report=html
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建Pull Request**
   - 使用PR模板
   - 详细描述更改内容
   - 链接相关Issues
   - 确保CI检查通过

## 代码规范

### Python代码风格

我们使用以下工具确保代码质量：

- **Black** - 代码格式化
- **flake8** - 代码检查
- **mypy** - 类型检查
- **isort** - 导入排序

### 提交信息规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型 (type):**
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例:**
```
feat(converter): add batch processing support

Add ability to process multiple files in a single operation.
This improves efficiency for users with many files to convert.

Closes #123
```

### 代码注释

- 所有公共API必须有docstring
- 复杂逻辑需要添加注释
- 使用中文注释（项目主要面向中文用户）

```python
def convert_clef_position(position: int, from_clef: str, to_clef: str) -> int:
    """
    转换不同谱号之间的五线谱位置
    
    Args:
        position: 原谱号中的位置
        from_clef: 源谱号类型
        to_clef: 目标谱号类型
        
    Returns:
        目标谱号中的位置
        
    Raises:
        ValueError: 当谱号类型不支持时
    """
```

## 测试指南

### 编写测试

- 为新功能编写单元测试
- 确保测试覆盖率不低于80%
- 使用有意义的测试名称
- 测试边界条件和错误情况

```python
def test_convert_alto_to_treble_basic():
    """测试基本的中音谱号到高音谱号转换"""
    converter = ClefConverter()
    result = converter.convert_alto_to_treble(test_notes)
    assert len(result) == len(test_notes)
    assert result[0].staff_position == expected_position
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_converter.py

# 运行特定测试
pytest tests/test_converter.py::test_convert_alto_to_treble_basic

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

## 文档贡献

### 文档类型

- **用户文档**: 使用说明、安装指南等
- **开发文档**: API文档、架构说明等
- **代码注释**: 函数和类的docstring

### 文档规范

- 使用Markdown格式
- 保持简洁明了
- 提供实际示例
- 及时更新过时内容

## 发布流程

项目维护者负责版本发布：

1. 更新版本号
2. 更新CHANGELOG.md
3. 创建Git标签
4. 发布到PyPI（如果适用）
5. 创建GitHub Release

## 行为准则

### 我们的承诺

为了营造开放和友好的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性别化语言或图像，以及不受欢迎的性关注或性骚扰
- 恶意评论、人身攻击或政治攻击
- 公开或私下骚扰
- 未经明确许可发布他人的私人信息
- 在专业环境中可能被认为不合适的其他行为

## 获得帮助

如果您需要帮助：

1. 查看 [文档](docs/)
2. 搜索现有 [Issues](https://github.com/your-username/clef-converter/issues)
3. 在 [Discussions](https://github.com/your-username/clef-converter/discussions) 中提问
4. 联系维护者

## 致谢

感谢所有为项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

再次感谢您的贡献！🎉
