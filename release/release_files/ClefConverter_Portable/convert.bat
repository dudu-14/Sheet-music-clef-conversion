@echo off
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
