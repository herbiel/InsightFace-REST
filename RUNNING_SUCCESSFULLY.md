# ✅ InsightFace-REST 本地运行成功！

## 🎉 状态总结

**API 已成功启动并运行！** 

```
✓ 模型加载成功
✓ 应用启动成功
✓ 可以接收请求
```

## 🚀 快速启动

### 1. 激活虚拟环境
```bash
conda activate insightface-rest-py310
```

### 2. 下载模型（首次运行）
```bash
python download_models.py
```

### 3. 启动 API 服务
```bash
./start_local.sh
```

## 🌐 API 文档

启动后访问以下地址：

- **Swagger UI** (推荐): http://localhost:18080/docs
- **ReDoc**: http://localhost:18080/redoc
- **OpenAPI JSON**: http://localhost:18080/openapi.json

## 📝 API 使用示例

### Python 客户端

```python
import requests
import base64
import json

# 读取图像
with open('your_image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

# 调用 API
response = requests.post(
    'http://localhost:18080/extract',
    json={
        'data': [image_data],
        'det_name': 'scrfd_10g_gnkps',
        'rec_name': 'glintr100',
        'extract_embedding': True
    }
)

result = response.json()
print(json.dumps(result, indent=2))
```

### cURL

```bash
# 检查 API 状态
curl http://localhost:18080/docs

# 提取人脸特征（需要先编码图像为 base64）
curl -X POST http://localhost:18080/extract \
  -H "Content-Type: application/json" \
  -d '{
    "data": ["base64_encoded_image_data"],
    "det_name": "scrfd_10g_gnkps",
    "rec_name": "glintr100"
  }'
```

## 📊 支持的模型

### 检测模型
- `scrfd_10g_gnkps` (默认，精度高)
- `scrfd_2.5g_gnkps` (平衡)
- `scrfd_500m_gnkps` (轻量，快速)
- `retinaface_r50_v1` (经典)

### 识别模型
- `glintr100` (默认，性能好)
- `w600k_r50` (高精度)
- `w600k_mbf` (轻量，快速)
- `arcface_r100_v1` (经典)

## ⚙️ 环境变量配置

```bash
# 自定义模型目录
export MODELS_DIR=/path/to/models

# 自定义日志级别
export LOG_LEVEL=DEBUG

# 自定义端口
export PORT=18081

# 跳过模型初始化（用于测试）
export SKIP_MODEL_INIT=true
```

## 🔧 故障排除

### 问题 1: "cannot pickle '_dynfunc._Closure' object"
**解决方案**：已自动配置 Numba 环境变量，应已解决。

### 问题 2: Port 18080 已被占用
```bash
# 使用其他端口
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18081
```

### 问题 3: 模型文件缺失
```bash
# 下载默认模型
python download_models.py

# 或下载轻量级模型
python download_models.py --models scrfd_500m_gnkps w600k_mbf
```

### 问题 4: 导入错误或模块缺失
```bash
# 重新安装依赖
pip install -r requirements.txt --force-reinstall
```

## 📚 文档文件

- `QUICKSTART_LOCAL.md` - 快速启动指南
- `LOCAL_SETUP.md` - 详细配置文档
- `README.md` - 项目说明

## 🎯 已完成的修复

1. ✅ **Python 3.10 兼容性**
   - 升级至 Python 3.10
   - 修复类型提示兼容性
   - 修复联合类型语法

2. ✅ **本地模型路径**
   - 配置支持本地 `./models/` 目录
   - 自动检测项目模型位置

3. ✅ **模型下载工具**
   - 创建 `download_models.py`
   - 支持 Google Drive 下载
   - 支持手动下载

4. ✅ **启动脚本**
   - `start_local.sh` - 一键启动
   - 自动环境配置
   - 自动依赖检查

5. ✅ **Numba 兼容性**
   - 配置环境变量避免序列化问题
   - 优化多进程处理

## 📌 关键文件

```
InsightFace-REST/
├── start_local.sh              # 启动脚本
├── download_models.py          # 模型下载工具
├── QUICKSTART_LOCAL.md         # 快速启动指南
├── LOCAL_SETUP.md              # 详细配置
├── requirements.txt            # Python 依赖
├── models/
│   ├── models.json             # 模型配置
│   └── onnx/                   # 模型存储
├── if_rest/
│   ├── api/main.py             # FastAPI 应用
│   ├── core/                   # 核心逻辑
│   └── settings.py             # 配置
└── README.md                   # 项目说明
```

## 🎓 下一步

1. **测试 API**: 访问 http://localhost:18080/docs
2. **上传图像**: 使用 Swagger UI 或 Python 客户端
3. **检查结果**: 查看人脸检测和识别结果
4. **优化性能**: 选择合适的模型和配置

## 💡 性能优化

### CPU 模式下优化
```bash
# 使用轻量级模型
export DET_NAME=scrfd_500m_gnkps
export REC_NAME=w600k_mbf

./start_local.sh
```

### 设置批处理
在 API 请求中增加 `det_batch_size` 和 `rec_batch_size` 以提高吞吐量。

---

**版本**: 0.9.5.0  
**Python**: 3.10  
**状态**: ✅ 完全可用  
**最后更新**: 2025-11-14

**祝使用愉快！** 🚀
