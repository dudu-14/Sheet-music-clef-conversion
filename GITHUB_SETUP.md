# GitHub 仓库设置指南

本文档指导您如何将本地的谱号转换器项目推送到GitHub。

## 1. 创建GitHub仓库

### 在GitHub网站上创建仓库

1. 登录 [GitHub](https://github.com)
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - **Repository name**: `clef-converter`
   - **Description**: `智能音乐识别和谱号转换工具 - 将中音谱号转换为高音谱号`
   - **Visibility**: Public（推荐）或 Private
   - **不要**勾选 "Initialize this repository with a README"
   - **不要**添加 .gitignore 或 license（我们已经有了）

4. 点击 "Create repository"

## 2. 连接本地仓库到GitHub

### 添加远程仓库

```bash
# 添加GitHub远程仓库（替换your-username为您的GitHub用户名）
git remote add origin https://github.com/your-username/clef-converter.git

# 验证远程仓库
git remote -v
```

### 推送代码到GitHub

```bash
# 推送主分支到GitHub
git push -u origin main
```

## 3. 配置仓库设置

### 3.1 启用GitHub Pages（可选）

如果您想为项目创建文档网站：

1. 进入仓库设置页面
2. 滚动到 "Pages" 部分
3. 选择 "Deploy from a branch"
4. 选择 "main" 分支和 "docs/" 文件夹
5. 点击 "Save"

### 3.2 设置分支保护规则

为了保护主分支：

1. 进入仓库设置页面
2. 点击左侧的 "Branches"
3. 点击 "Add rule"
4. 配置规则：
   - Branch name pattern: `main`
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators

### 3.3 配置Secrets（用于CI/CD）

如果您计划使用自动化部署：

1. 进入仓库设置页面
2. 点击左侧的 "Secrets and variables" > "Actions"
3. 添加以下secrets：
   - `DOCKER_USERNAME`: Docker Hub用户名
   - `DOCKER_PASSWORD`: Docker Hub密码
   - `PYPI_API_TOKEN`: PyPI API令牌（如果要发布到PyPI）

## 4. 设置Issue和PR模板

### 4.1 创建Issue模板

GitHub会自动识别 `.github/ISSUE_TEMPLATE/` 目录中的模板。

### 4.2 创建Pull Request模板

创建 `.github/pull_request_template.md` 文件：

```markdown
## 变更描述

请简要描述此PR的变更内容。

## 变更类型

- [ ] Bug修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能优化
- [ ] 代码重构
- [ ] 其他（请说明）

## 测试

- [ ] 已添加单元测试
- [ ] 已运行现有测试
- [ ] 已手动测试

## 检查清单

- [ ] 代码遵循项目规范
- [ ] 已更新相关文档
- [ ] 已添加必要的注释
- [ ] 没有引入新的警告
```

## 5. 配置GitHub Actions

我们已经创建了 `.github/workflows/ci.yml` 文件，它会自动：

- 在多个Python版本和操作系统上运行测试
- 检查代码质量
- 生成覆盖率报告
- 构建Docker镜像
- 发布到PyPI（在发布时）

## 6. 添加徽章到README

更新README.md中的徽章URL：

```markdown
[![Build Status](https://github.com/your-username/clef-converter/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/your-username/clef-converter/actions)
[![Coverage](https://codecov.io/gh/your-username/clef-converter/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/clef-converter)
[![PyPI version](https://badge.fury.io/py/clef-converter.svg)](https://badge.fury.io/py/clef-converter)
[![Docker](https://img.shields.io/docker/pulls/your-username/clef-converter.svg)](https://hub.docker.com/r/your-username/clef-converter)
```

## 7. 设置协作者

如果这是团队项目：

1. 进入仓库设置页面
2. 点击左侧的 "Collaborators"
3. 点击 "Add people"
4. 输入GitHub用户名或邮箱
5. 选择权限级别（Read, Write, Admin）

## 8. 创建第一个Release

当您准备发布第一个版本时：

1. 进入仓库主页
2. 点击右侧的 "Releases"
3. 点击 "Create a new release"
4. 填写信息：
   - **Tag version**: `v1.0.0`
   - **Release title**: `v1.0.0 - 初始发布版本`
   - **Description**: 描述此版本的主要功能
5. 点击 "Publish release"

## 9. 设置项目管理

### 9.1 启用Projects

1. 进入仓库主页
2. 点击 "Projects" 标签
3. 点击 "New project"
4. 选择模板或创建空白项目

### 9.2 设置Milestones

1. 进入 "Issues" 页面
2. 点击 "Milestones"
3. 创建里程碑（如 "v1.1.0", "v2.0.0"）

## 10. 社区文件

确保以下文件存在并且内容完整：

- ✅ `README.md` - 项目介绍
- ✅ `LICENSE` - 许可证
- ✅ `CONTRIBUTING.md` - 贡献指南
- ✅ `CHANGELOG.md` - 更新日志
- ✅ `CODE_OF_CONDUCT.md` - 行为准则（可选）
- ✅ `SECURITY.md` - 安全政策（可选）

## 完成！

现在您的GitHub仓库已经完全设置好了。您可以：

- 邀请其他开发者协作
- 接受Pull Requests
- 跟踪Issues
- 自动化CI/CD流程
- 发布新版本

## 下一步

1. 更新README中的GitHub链接
2. 设置Codecov集成
3. 配置Docker Hub自动构建
4. 设置PyPI发布流程
5. 创建项目网站

---

**提示**: 记得将所有示例中的 `your-username` 替换为您的实际GitHub用户名！
