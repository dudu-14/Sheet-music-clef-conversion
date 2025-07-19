#!/usr/bin/env python3
"""
谱号转换器主程序
支持命令行和Web界面两种使用方式
"""

import argparse
import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.converter import ClefConverter
from src.utils.logger import setup_logger
from src.web.app import create_app


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="谱号转换器 - 将中音谱号转换为高音谱号",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py input.png -o output.png                    # 基本转换
  python main.py *.png -o output_dir/ --batch              # 批量处理
  python main.py input.png -o output --formats png,pdf     # 多格式输出
  python main.py --web                                     # 启动Web界面
        """
    )
    
    # 基本参数
    parser.add_argument(
        'input', 
        nargs='?',
        help='输入图片路径或模式'
    )
    parser.add_argument(
        '-o', '--output', 
        help='输出路径'
    )
    
    # 输出选项
    parser.add_argument(
        '--formats', 
        default='png',
        help='输出格式，用逗号分隔 (png,pdf,midi)'
    )
    
    # 处理选项
    parser.add_argument(
        '--batch', 
        action='store_true',
        help='批量处理模式'
    )
    parser.add_argument(
        '--high-quality', 
        action='store_true',
        help='高精度模式（处理时间更长）'
    )
    
    # Web模式
    parser.add_argument(
        '--web', 
        action='store_true',
        help='启动Web界面'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=5000,
        help='Web服务端口 (默认: 5000)'
    )
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Web服务主机 (默认: 127.0.0.1)'
    )
    
    # 其他选项
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true',
        help='详细输出'
    )
    parser.add_argument(
        '--version', 
        action='version',
        version='谱号转换器 v1.0.0'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logger(verbose=args.verbose)
    
    # Web模式
    if args.web:
        print(f"启动Web界面: http://{args.host}:{args.port}")
        app = create_app()
        app.run(host=args.host, port=args.port, debug=args.verbose)
        return
    
    # 命令行模式
    if not args.input:
        parser.error("请提供输入图片路径，或使用 --web 启动Web界面")
    
    if not args.output:
        parser.error("请提供输出路径")
    
    try:
        # 创建转换器
        converter = ClefConverter(
            high_quality=args.high_quality,
            verbose=args.verbose
        )
        
        # 执行转换
        if args.batch:
            converter.convert_batch(
                input_pattern=args.input,
                output_dir=args.output,
                formats=args.formats.split(',')
            )
        else:
            converter.convert_single(
                input_path=args.input,
                output_path=args.output,
                formats=args.formats.split(',')
            )
            
        print("转换完成！")
        
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
