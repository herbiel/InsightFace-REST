# 不使用 Docker 的本地运行指南

本文档介绍如何在 macOS 本地直接运行 InsightFace-REST，无需 Docker。

## 前置需求

1. **Python 3.10+** （推荐，已配置为默认）
2. **pip** 包管理器
3. **Conda**（用于管理虚拟环境）
4. 网络连接（用于从 Google Drive 下载模型）

## 安装步骤

### 1. 创建虚拟环境（已预配置）

```bash
# 激活已创建的 Python 3.10 虚拟环境
conda activate insightface-rest-py310

# 验证 Python 版本（应为 3.10+）
python --version
```

### 2. 安装依赖

```bash
# 使用国内镜像加速（推荐）
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 或使用默认源
pip install -r requirements.txt
```

### 3. 下载模型文件

模型文件位置：`./models/onnx/`

**方式 1：自动下载（推荐）**

```bash
# 下载默认模型（scrfd_10g_gnkps + glintr100）
python download_models.py

# 下载特定模型
python download_models.py --det scrfd_10g_gnkps
python download_models.py --rec glintr100

# 下载所有模型
python download_models.py --all
```

**方式 2：手动下载**

从 `models/models.json` 中找到模型的 Google Drive 链接，手动下载并放置到对应目录：

```
models/
├── onnx/
│   ├── scrfd_10g_gnkps/
│   │   └── scrfd_10g_gnkps.onnx
│   ├── glintr100/
│   │   └── glintr100.onnx
│   └── ...
└── models.json
```

**方式 3：使用轻量级模型**

如果 Google Drive 无法访问，可以修改 `if_rest/settings.py` 使用更轻量的模型：

```python
# 修改默认模型
det_name='scrfd_500m_gnkps'  # 更小的检测模型
rec_name='w600k_mbf'         # 更快的识别模型
```

### 4. 启动 API 服务

#### 方式 1：使用 Uvicorn（轻量级，推荐用于开发）

```bash
cd /Users/habi/InsightFace-REST
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080 --reload
```

- `--reload`：代码变更时自动重启（开发模式）
- 访问 API 文档：http://localhost:18080/docs

#### 方式 2：使用 Gunicorn + Uvicorn（生产级，多 worker）

```bash
cd /Users/habi/InsightFace-REST

# 自动下载模型（可选，第一次运行时）
python -m if_rest.prepare_models

# 启动服务（默认 4 个 worker）
gunicorn -w 4 -k uvicorn.workers.UvicornWorker --keep-alive 60 --timeout 60 if_rest.api.main:app -b 0.0.0.0:18080
```

## 快速启动脚本

已为你创建了 `start_local.sh` 脚本，可以一键启动：

```bash
./start_local.sh
```

脚本会自动：
1. 激活虚拟环境
2. 检查依赖
3. 验证模型配置
4. 启动 FastAPI 服务

或直接运行：

```bash
conda activate insightface-rest-py310
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080 --reload
```

## 环境变量配置

可以通过环境变量自定义配置：

```bash
# 自定义模型目录
export MODELS_DIR=/path/to/models

# 自定义日志级别
export LOG_LEVEL=info

# 自定义 worker 数量
export NUM_WORKERS=4

# 然后启动服务
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080
```

## 首次运行

第一次运行时，API 会自动：
1. 检查模型是否存在
2. 必要时从 Google Drive 或其他源下载模型
3. 初始化推理引擎

**注意**：如果在中国大陆环境，Google Drive 可能无法访问。此时需要手动下载模型或使用代理。

## 常见问题

### Q1: ModuleNotFoundError
**问题**：缺少某个 Python 模块

**解决**：
```bash
pip install <module_name>
```

### Q2: 模型下载失败
**问题**：Google Drive 无法访问或下载超时

**解决**：
- 方式 1：使用代理或 VPN 访问 Google Drive
- 方式 2：手动下载模型到 `./models/onnx/` 目录
- 方式 3：使用 `models.override.json` 指定本地模型路径

### Q3: Port 18080 already in use
**问题**：端口被占用

**解决**：
```bash
# 使用其他端口
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18081

# 或杀死占用该端口的进程
lsof -i :18080
kill -9 <PID>
```

### Q4: 内存不足
**问题**：运行时 OOM

**解决**：
- 减少 worker 数量：`-w 2` 替代 `-w 4`
- 禁用批处理或减少批大小
- 增加系统虚拟内存

## API 使用示例

### Python 客户端

```python
import requests
import base64

# 读取图像
with open('test.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

# 调用 API
response = requests.post(
    'http://localhost:18080/extract',
    json={
        'data': image_data,
        'det_name': 'retinaface_r50_v1',
        'rec_name': 'arcface_r100_v1'
    }
)

print(response.json())
```

### cURL

```bash
# 检查 API 是否运行
curl http://localhost:18080/docs

# 提取人脸特征
curl -X POST http://localhost:18080/extract \
  -H "Content-Type: application/json" \
  -d '{
    "data": "base64_encoded_image",
    "det_name": "retinaface_r50_v1",
    "rec_name": "arcface_r100_v1"
  }'
```

## 配置修复说明

已修改 `if_rest/core/configs.py` 支持本地开发：
- 默认尝试加载项目内 `./models/models.json`
- 如不存在则回退到 `/models/models.json`（Docker 路径）
- 可通过 `MODELS_DIR` 环境变量覆盖

## 更多文档

- API 文档：http://localhost:18080/docs（运行时访问）
- 模型配置：`./models/models.json`
- 主要代码：`if_rest/api/main.py`（FastAPI 应用入口）

---

**快速开始命令**：

```bash
# 1. 安装依赖
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 2. 启动服务
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080 --reload

# 3. 访问 API
# 浏览器：http://localhost:18080/docs
```

祝使用愉快！🚀
