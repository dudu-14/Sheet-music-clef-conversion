# API 文档

本文档描述了谱号转换器的Web API接口和Python编程接口。

## Web API

### 基础信息

- **基础URL**: `http://localhost:5000`
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`
- **认证**: 无需认证（本地使用）

### 通用响应格式

#### 成功响应
```json
{
    "success": true,
    "data": {...},
    "message": "操作成功"
}
```

#### 错误响应
```json
{
    "success": false,
    "error": "错误描述",
    "code": "ERROR_CODE"
}
```

### 端点列表

#### 1. 健康检查

**GET** `/api/health`

检查API服务状态。

**响应示例**:
```json
{
    "status": "healthy",
    "timestamp": 1640995200.123,
    "version": "1.0.0"
}
```

#### 2. 获取支持格式

**GET** `/api/formats`

获取支持的输入和输出格式。

**响应示例**:
```json
{
    "input_formats": ["png", "jpg", "jpeg", "bmp", "tiff", "tif", "gif"],
    "output_formats": ["png", "pdf", "midi", "svg"]
}
```

#### 3. 文件上传

**POST** `/upload`

上传乐谱图片文件。

**请求参数**:
- `file`: 图片文件（multipart/form-data）
- `high_quality`: 是否启用高精度模式（可选，默认false）
- `formats`: 输出格式，逗号分隔（可选，默认png）

**响应示例**:
```json
{
    "task_id": "uuid-string",
    "filename": "score.png",
    "message": "文件上传成功"
}
```

#### 4. 开始转换

**POST** `/convert/{task_id}`

开始转换任务。

**路径参数**:
- `task_id`: 任务ID

**请求体**:
```json
{
    "high_quality": false,
    "formats": ["png", "pdf"]
}
```

**响应示例**:
```json
{
    "message": "转换任务已启动"
}
```

#### 5. 查询状态

**GET** `/status/{task_id}`

查询转换任务状态。

**路径参数**:
- `task_id`: 任务ID

**响应示例**:
```json
{
    "status": "processing",
    "progress": 65,
    "message": "正在识别音符...",
    "notes_count": 0,
    "processing_time": 0,
    "output_files": []
}
```

**状态值**:
- `uploaded`: 文件已上传
- `processing`: 正在处理
- `completed`: 转换完成
- `failed`: 转换失败

#### 6. 下载文件

**GET** `/download/{task_id}/{format}`

下载转换结果文件。

**路径参数**:
- `task_id`: 任务ID
- `format`: 文件格式（png, pdf, midi等）

**响应**: 文件下载

#### 7. 清理任务

**DELETE** `/cleanup/{task_id}`

清理任务文件。

**路径参数**:
- `task_id`: 任务ID

**响应示例**:
```json
{
    "message": "任务清理完成"
}
```

#### 8. 快速转换

**POST** `/api/convert/quick`

同步快速转换（适用于小文件）。

**请求参数**:
- `file`: 图片文件（multipart/form-data）
- `high_quality`: 是否启用高精度模式（可选）
- `formats`: 输出格式，逗号分隔（可选）

**响应示例**:
```json
{
    "success": true,
    "notes_count": 24,
    "processing_time": 2.5,
    "output_files": ["png", "midi"],
    "download_urls": {
        "png": "/api/download/temp/result.png",
        "midi": "/api/download/temp/result.midi"
    }
}
```

#### 9. 批量转换

**POST** `/api/convert/batch`

批量转换多个文件。

**请求参数**:
- `files`: 多个图片文件（multipart/form-data）
- `high_quality`: 是否启用高精度模式（可选）
- `formats`: 输出格式，逗号分隔（可选）

**响应示例**:
```json
{
    "task_id": "batch-uuid",
    "total_files": 5,
    "successful_count": 4,
    "failed_count": 1,
    "total_notes": 120,
    "results": [
        {
            "filename": "score1.png",
            "success": true,
            "notes_count": 30,
            "output_files": ["png", "midi"]
        }
    ]
}
```

#### 10. 系统统计

**GET** `/api/stats`

获取系统统计信息。

**响应示例**:
```json
{
    "total_conversions": 1234,
    "total_notes_converted": 56789,
    "average_processing_time": 2.5,
    "supported_formats": {
        "input": ["png", "jpg", "jpeg", "bmp", "tiff", "tif", "gif"],
        "output": ["png", "pdf", "midi", "svg"]
    },
    "system_info": {
        "version": "1.0.0",
        "uptime": 86400,
        "memory_usage": "256MB",
        "cpu_usage": "15%"
    }
}
```

### 错误代码

| 代码 | 说明 |
|------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 415 | 不支持的文件格式 |
| 500 | 服务器内部错误 |

## Python API

### 核心类

#### ClefConverter

主转换器类，提供完整的转换功能。

```python
from src.core.converter import ClefConverter

# 创建转换器
converter = ClefConverter(
    high_quality=False,
    verbose=False,
    temp_dir=None
)

# 转换单个文件
result = converter.convert_single(
    input_path="input.png",
    output_path="output.png",
    formats=["png", "pdf"],
    progress_callback=None
)

# 批量转换
result = converter.convert_batch(
    input_pattern="*.png",
    output_dir="output/",
    formats=["png"],
    progress_callback=None
)

# 清理资源
converter.cleanup()
```

#### 使用上下文管理器

```python
with ClefConverter(high_quality=True) as converter:
    result = converter.convert_single("input.png", "output.png")
    print(f"转换完成，识别到 {result['notes_count']} 个音符")
```

### 数据模型

#### Note

音符数据模型。

```python
from src.models.note import Note

note = Note(
    pitch=60,           # MIDI音高值
    start_time=0.0,     # 开始时间（秒）
    duration=1.0,       # 持续时间（秒）
    velocity=80,        # 力度
    staff_position=0,   # 五线谱位置
    accidental="",      # 升降号
    tie=False,          # 连音线
    dot=False           # 附点
)
```

#### ScoreMetadata

乐谱元数据模型。

```python
from src.models.score_metadata import ScoreMetadata

metadata = ScoreMetadata(
    time_signature=(4, 4),  # 拍号
    key_signature="C",      # 调号
    tempo=120,              # 速度
    clef_type="alto",       # 谱号类型
    title="乐曲标题",       # 标题
    composer="作曲家"       # 作曲家
)
```

#### RecognitionResult

识别结果模型。

```python
from src.models.recognition_result import RecognitionResult

result = RecognitionResult(
    notes=[],           # 音符列表
    metadata=metadata,  # 元数据
    measures=[],        # 小节列表
    confidence=0.95,    # 识别置信度
    processing_time=2.5 # 处理时间
)
```

### 工具函数

#### 文件工具

```python
from src.utils.file_utils import (
    validate_image_file,
    validate_output_format,
    generate_output_path,
    find_image_files
)

# 验证图像文件
is_valid = validate_image_file("image.png")

# 查找图像文件
image_files = list(find_image_files("directory/"))
```

#### 图像工具

```python
from src.utils.image_utils import (
    load_image,
    save_image,
    resize_image,
    enhance_image
)

# 加载和处理图像
image = load_image("input.png")
enhanced = enhance_image(image, brightness=1.2)
save_image(enhanced, "output.png")
```

#### 音乐工具

```python
from src.utils.music_utils import (
    midi_to_note_name,
    note_name_to_midi,
    calculate_staff_position,
    convert_clef_position
)

# 音符转换
note_name = midi_to_note_name(60)  # "C4"
midi_pitch = note_name_to_midi("C4")  # 60

# 谱号位置转换
treble_pos = convert_clef_position(0, "alto", "treble")
```

### 进度回调

```python
def progress_callback(progress_data):
    """
    进度回调函数
    
    Args:
        progress_data: 进度数据字典
            - step: 当前步骤
            - total: 总步骤数
            - operation: 当前操作描述
            - percentage: 完成百分比
            - elapsed_time: 已用时间
    """
    print(f"进度: {progress_data['percentage']:.1f}% - {progress_data['operation']}")

# 使用进度回调
result = converter.convert_single(
    "input.png", 
    "output.png", 
    progress_callback=progress_callback
)
```

### 异常处理

```python
from src.core.converter import ClefConverter

try:
    with ClefConverter() as converter:
        result = converter.convert_single("input.png", "output.png")
        
        if result['success']:
            print(f"转换成功！识别到 {result['notes_count']} 个音符")
        else:
            print(f"转换失败: {result['error']}")
            
except FileNotFoundError:
    print("输入文件不存在")
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
```

## 客户端示例

### JavaScript (Web)

```javascript
// 上传文件并转换
async function convertFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('high_quality', 'true');
    formData.append('formats', 'png,midi');
    
    try {
        // 上传文件
        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const uploadData = await uploadResponse.json();
        
        // 开始转换
        const convertResponse = await fetch(`/convert/${uploadData.task_id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                high_quality: true,
                formats: ['png', 'midi']
            })
        });
        
        // 监控进度
        const taskId = uploadData.task_id;
        const interval = setInterval(async () => {
            const statusResponse = await fetch(`/status/${taskId}`);
            const statusData = await statusResponse.json();
            
            console.log(`进度: ${statusData.progress}%`);
            
            if (statusData.status === 'completed') {
                clearInterval(interval);
                console.log('转换完成！');
                
                // 下载文件
                statusData.output_files.forEach(format => {
                    const downloadUrl = `/download/${taskId}/${format}`;
                    window.open(downloadUrl);
                });
            }
        }, 1000);
        
    } catch (error) {
        console.error('转换失败:', error);
    }
}
```

### Python (客户端)

```python
import requests
import time

def convert_file_api(file_path, output_formats=['png']):
    """使用API转换文件"""
    base_url = "http://localhost:5000"
    
    # 上传文件
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'high_quality': 'true',
            'formats': ','.join(output_formats)
        }
        
        response = requests.post(f"{base_url}/upload", files=files, data=data)
        upload_result = response.json()
        
        if not upload_result.get('task_id'):
            raise Exception("上传失败")
        
        task_id = upload_result['task_id']
    
    # 开始转换
    convert_data = {
        'high_quality': True,
        'formats': output_formats
    }
    response = requests.post(f"{base_url}/convert/{task_id}", json=convert_data)
    
    # 监控进度
    while True:
        response = requests.get(f"{base_url}/status/{task_id}")
        status = response.json()
        
        print(f"进度: {status['progress']}% - {status['message']}")
        
        if status['status'] == 'completed':
            print(f"转换完成！识别到 {status['notes_count']} 个音符")
            
            # 下载文件
            for format_name in status['output_files']:
                download_url = f"{base_url}/download/{task_id}/{format_name}"
                response = requests.get(download_url)
                
                with open(f"output.{format_name}", 'wb') as f:
                    f.write(response.content)
                    
            break
            
        elif status['status'] == 'failed':
            raise Exception(f"转换失败: {status.get('error')}")
            
        time.sleep(1)

# 使用示例
convert_file_api("score.png", ["png", "pdf", "midi"])
```

## 限制和注意事项

1. **文件大小限制**: 最大100MB
2. **并发限制**: 同时最多处理10个任务
3. **超时设置**: 单个任务最长5分钟
4. **临时文件**: 自动清理1小时后的临时文件
5. **内存使用**: 大文件可能需要大量内存

## 版本兼容性

- **API版本**: v1.0
- **向后兼容**: 保证主版本内的向后兼容性
- **废弃通知**: 废弃功能将提前一个版本通知
