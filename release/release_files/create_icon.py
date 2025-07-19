"""
创建应用程序图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """创建应用程序图标"""
    
    # 创建256x256的图像
    size = 256
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景圆形
    margin = 20
    draw.ellipse([margin, margin, size-margin, size-margin], 
                fill=(70, 130, 180, 255), outline=(30, 90, 140, 255), width=4)
    
    # 绘制音符符号
    # 五线谱
    line_color = (255, 255, 255, 255)
    line_width = 3
    staff_start = 80
    staff_end = 180
    line_spacing = 15
    
    for i in range(5):
        y = staff_start + i * line_spacing
        draw.line([60, y, 196, y], fill=line_color, width=line_width)
    
    # 中音谱号符号（简化版）
    clef_x = 80
    clef_y = staff_start + 2 * line_spacing
    
    # 绘制中音谱号的基本形状
    draw.ellipse([clef_x-8, clef_y-10, clef_x+8, clef_y+10], 
                fill=line_color, outline=line_color)
    draw.rectangle([clef_x-2, clef_y-20, clef_x+2, clef_y+20], 
                  fill=line_color)
    
    # 箭头表示转换
    arrow_start_x = 120
    arrow_end_x = 140
    arrow_y = clef_y
    
    # 箭头主体
    draw.line([arrow_start_x, arrow_y, arrow_end_x, arrow_y], 
             fill=(255, 215, 0, 255), width=4)
    
    # 箭头头部
    draw.polygon([
        (arrow_end_x, arrow_y),
        (arrow_end_x-8, arrow_y-6),
        (arrow_end_x-8, arrow_y+6)
    ], fill=(255, 215, 0, 255))
    
    # 高音谱号符号（简化版）
    treble_x = 160
    treble_y = clef_y
    
    # 绘制高音谱号的基本形状
    draw.ellipse([treble_x-6, treble_y-15, treble_x+6, treble_y-3], 
                fill=line_color, outline=line_color)
    draw.line([treble_x, treble_y-15, treble_x, treble_y+15], 
             fill=line_color, width=3)
    draw.ellipse([treble_x-4, treble_y+8, treble_x+4, treble_y+16], 
                fill=line_color, outline=line_color)
    
    # 保存为ICO格式
    # 创建多个尺寸的图标
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    
    for icon_size in sizes:
        resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
        images.append(resized)
    
    # 保存ICO文件
    img.save('icon.ico', format='ICO', sizes=[(s, s) for s in sizes])
    print("✅ 图标文件已创建: icon.ico")
    
    # 也保存为PNG格式
    img.save('icon.png', format='PNG')
    print("✅ PNG图标已创建: icon.png")

if __name__ == '__main__':
    try:
        create_icon()
    except Exception as e:
        print(f"❌ 创建图标失败: {e}")
        print("继续打包过程...")
