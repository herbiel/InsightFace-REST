# 🚀 InsightFace-REST 本地快速启动

## 环境已配置完毕！

Python 3.10 虚拟环境已创建：`insightface-rest-py310`

## 3 步快速启动

### 1️⃣ 激活虚拟环境
```bash
conda activate insightface-rest-py310
```

### 2️⃣ 下载模型（首次运行）
```bash
python download_models.py
```

### 3️⃣ 启动服务
```bash
./start_local.sh
```

或直接运行：
```bash
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080 --reload
```

## 访问 API

- **API 文档**: http://localhost:18080/docs
- **API 地址**: http://localhost:18080
- **OpenAPI 规范**: http://localhost:18080/openapi.json

## 完整指南

详见 [LOCAL_SETUP.md](./LOCAL_SETUP.md)

## 模型下载选项

```bash
# 下载默认模型（推荐）
python download_models.py

# 下载特定模型
python download_models.py --det scrfd_10g_gnkps --rec glintr100

# 下载所有模型
python download_models.py --all

# 下载轻量级模型
python download_models.py --det scrfd_500m_gnkps --rec w600k_mbf
```

## 故障排除

### 问题 1: ModuleNotFoundError

重新安装依赖：
```bash
pip install -r requirements.txt
```

### 问题 2: 模型下载失败（Google Drive 无法访问）

手动下载模型：
1. 查看 `models/models.json` 中的下载链接
2. 使用浏览器或代理下载
3. 放置到 `models/onnx/<model_name>/` 目录

### 问题 3: Port 18080 already in use

使用其他端口：
```bash
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18081
```

## 常用命令速查

| 任务 | 命令 |
|------|------|
| 激活环境 | `conda activate insightface-rest-py310` |
| 下载模型 | `python download_models.py` |
| 启动服务 | `./start_local.sh` 或 `uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080` |
| 查看日志 | 服务启动时自动显示 |
| 停止服务 | 按 `Ctrl+C` |
| 查看 API 文档 | 浏览器打开 http://localhost:18080/docs |

---

**版本**: 0.9.5.0  
**Python**: 3.10+  
**最后更新**: 2025-11-14
