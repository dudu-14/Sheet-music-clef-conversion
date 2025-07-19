# 示例文件

这个目录包含了谱号转换器的示例文件和使用案例。

## 文件说明

- `sample_alto_clef.png` - 示例中音谱号乐谱图片
- `expected_treble_clef.png` - 期望的高音谱号转换结果
- `test_batch/` - 批量处理测试文件
- `results/` - 转换结果示例

## 使用方法

### 单个文件转换
```bash
python main.py examples/sample_alto_clef.png -o examples/results/converted.png
```

### 批量转换
```bash
python main.py examples/test_batch/*.png -o examples/results/ --batch
```

### Web界面测试
1. 启动Web服务: `python main.py --web`
2. 在浏览器中打开 http://127.0.0.1:5000
3. 上传 `sample_alto_clef.png` 进行测试

## 测试数据

示例文件来源于公开的音乐教育资源，用于验证系统的识别和转换准确性。
