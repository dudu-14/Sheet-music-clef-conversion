"""
PyInstaller打包脚本
用于将谱号转换器打包成可执行文件
"""

import os
import sys
import shutil
from pathlib import Path


def create_spec_file():
    """创建PyInstaller spec文件"""

    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent

# 数据文件收集
datas = [
    # Web模板和静态文件
    (str(project_root / 'src' / 'web' / 'templates'), 'src/web/templates'),
    (str(project_root / 'src' / 'web' / 'static'), 'src/web/static'),
    
    # 文档文件
    (str(project_root / 'docs'), 'docs'),
    
    # 示例文件
    (str(project_root / 'examples'), 'examples'),
    
    # 配置文件
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
]

# 隐藏导入
hiddenimports = [
    'src.core.converter',
    'src.core.omr_engine',
    'src.core.midi_converter',
    'src.core.clef_converter',
    'src.core.score_renderer',
    'src.core.image_preprocessor',
    'src.models.note',
    'src.models.score_metadata',
    'src.models.recognition_result',
    'src.models.measure',
    'src.utils.logger',
    'src.utils.file_utils',
    'src.utils.image_utils',
    'src.utils.music_utils',
    'src.web.app',
    'src.web.routes',
    'flask',
    'flask.templating',
    'jinja2',
    'werkzeug',
    'PIL',
    'PIL._tkinter_finder',
    'cv2',
    'numpy',
    'music21',
    'mido',
    'matplotlib',
    'scipy',
]

# 排除的模块
excludes = [
    'tkinter',
    'test',
    'unittest',
    'pdb',
    'doctest',
    'difflib',
]

# 分析配置
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

# 去除重复文件
pyz = PYZ(a.pure)

# 可执行文件配置
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ClefConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if Path('icon.ico').exists() else None,
)

# 目录打包（可选）
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='ClefConverter'
# )
"""

    with open("clef_converter.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)

    print("✅ PyInstaller spec文件已创建: clef_converter.spec")


def build_executable():
    """构建可执行文件"""

    print("🚀 开始构建可执行文件...")

    # 确保release目录存在
    release_dir = Path("release")
    release_dir.mkdir(exist_ok=True)

    # 清理之前的构建
    if os.path.exists("build"):
        shutil.rmtree("build")
        print("🧹 清理build目录")

    if os.path.exists("dist"):
        shutil.rmtree("dist")
        print("🧹 清理dist目录")

    # 运行PyInstaller
    os.system("pyinstaller clef_converter.spec --clean --noconfirm")

    # 移动可执行文件到release目录
    if Path("dist/ClefConverter.exe").exists():
        shutil.move("dist/ClefConverter.exe", release_dir / "ClefConverter.exe")
        print(f"📦 可执行文件已移动到: {release_dir.absolute()}")

    print("✅ 构建完成！")


def create_portable_package():
    """创建便携版包"""

    print("📦 创建便携版包...")

    # 创建便携版目录
    portable_dir = Path("ClefConverter_Portable")
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir()

    # 复制可执行文件
    if Path("dist/ClefConverter.exe").exists():
        shutil.copy2("dist/ClefConverter.exe", portable_dir)

    # 复制必要文件
    files_to_copy = ["README.md", "LICENSE", "CHANGELOG.md", "docs", "examples"]

    for item in files_to_copy:
        src = Path(item)
        if src.exists():
            if src.is_file():
                shutil.copy2(src, portable_dir)
            else:
                shutil.copytree(src, portable_dir / src.name)

    # 创建启动脚本
    start_script = portable_dir / "start.bat"
    start_script.write_text(
        """@echo off
echo 谱号转换器 - Clef Converter
echo ============================
echo.
echo 启动Web界面...
ClefConverter.exe --web
pause
""",
        encoding="utf-8",
    )

    # 创建命令行脚本
    cli_script = portable_dir / "convert.bat"
    cli_script.write_text(
        """@echo off
echo 谱号转换器命令行模式
echo 用法: convert.bat input.png output.png
echo.
if "%1"=="" (
    echo 请提供输入文件路径
    pause
    exit /b 1
)
if "%2"=="" (
    echo 请提供输出文件路径
    pause
    exit /b 1
)
ClefConverter.exe "%1" -o "%2"
pause
""",
        encoding="utf-8",
    )

    print(f"✅ 便携版包已创建: {portable_dir.absolute()}")


if __name__ == "__main__":
    print("🎵 谱号转换器 - 打包工具")
    print("=" * 40)

    try:
        # 创建spec文件
        create_spec_file()

        # 构建可执行文件
        build_executable()

        # 创建便携版包
        create_portable_package()

        print("\n🎉 打包完成！")
        print("\n📁 输出文件:")
        print(f"   - 可执行文件: dist/ClefConverter.exe")
        print(f"   - 便携版包: ClefConverter_Portable/")

    except Exception as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)
