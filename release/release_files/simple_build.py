"""
简化的PyInstaller构建脚本
"""

import os
import sys
import shutil
from pathlib import Path

def build_executable():
    """使用简单的PyInstaller命令构建可执行文件"""
    
    print("🎵 谱号转换器 - 简化构建")
    print("=" * 40)
    
    # 回到项目根目录
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    print(f"📁 工作目录: {project_root}")
    
    # 清理之前的构建
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 清理 {dir_name} 目录")
    
    # 简单的构建命令
    cmd = 'pyinstaller --onefile --name=ClefConverter main.py'
    
    print("🚀 开始构建...")
    print(f"📝 命令: {cmd}")
    
    # 执行构建
    result = os.system(cmd)
    
    if result == 0:
        print("✅ 构建成功！")
        
        # 移动文件到release目录
        release_dir = project_root / 'release' / '1.0.0'
        release_dir.mkdir(exist_ok=True)
        
        exe_source = project_root / 'dist' / 'ClefConverter.exe'
        exe_target = release_dir / 'ClefConverter.exe'
        
        if exe_source.exists():
            if exe_target.exists():
                exe_target.unlink()
            shutil.move(str(exe_source), str(exe_target))
            print(f"📦 可执行文件已移动到: {exe_target}")
            
            # 创建便携版包
            create_portable_package(release_dir, exe_target)
            
            return True
        else:
            print("❌ 未找到生成的可执行文件")
            return False
    else:
        print("❌ 构建失败")
        return False

def create_portable_package(release_dir, exe_path):
    """创建便携版包"""
    
    print("📦 创建便携版包...")
    
    portable_dir = release_dir / 'ClefConverter_Portable'
    if portable_dir.exists():
        shutil.rmtree(portable_dir)
    
    portable_dir.mkdir()
    
    # 复制可执行文件
    shutil.copy2(exe_path, portable_dir / 'ClefConverter.exe')
    
    # 创建启动脚本
    start_script = portable_dir / 'start_web.bat'
    start_script.write_text('''@echo off
title 谱号转换器 - Clef Converter
echo.
echo ====================================
echo    谱号转换器 - Clef Converter
echo ====================================
echo.
echo 正在启动Web界面...
echo 请稍候，浏览器将自动打开
echo.

ClefConverter.exe --web

echo.
echo 按任意键退出...
pause >nul
''', encoding='utf-8')
    
    print(f"✅ 便携版包已创建: {portable_dir}")

if __name__ == '__main__':
    try:
        success = build_executable()
        if success:
            print("\n🎉 构建完成！")
            print("\n📁 输出文件:")
            print("   - release/1.0.0/ClefConverter.exe")
            print("   - release/1.0.0/ClefConverter_Portable/")
        else:
            print("\n❌ 构建失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 构建过程中出错: {e}")
        sys.exit(1)
