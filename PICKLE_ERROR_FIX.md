# 🔧 Pickle 错误 - 故障排除指南

## 问题描述

```
{
  "detail": "cannot pickle '_dynfunc._Closure' object"
}
```

## 原因分析

这是由于：
1. Numba JIT 编译的函数无法被序列化（pickle）
2. Uvicorn 的 `--reload` 选项会启用多进程，导致需要序列化 Numba 函数
3. 多进程模式下的 worker 进程无法反序列化这些函数

## ✅ 已应用的修复

### 1. 禁用热重载（Reload）
已从 `start_local.sh` 中移除 `--reload` 选项：
```bash
# ❌ 之前（导致问题）
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080 --reload

# ✅ 现在（修复）
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080
```

### 2. 配置 Numba 环境变量
在启动脚本中设置：
```bash
export NUMBA_CACHE_DIR=/tmp/numba_cache
export NUMBA_DISABLE_JIT=0
```

### 3. 创建专用启动脚本
创建了 `run_local.py` 作为备选启动方式

## 🚀 正确的启动方式

### 方式 1：使用 Shell 脚本（推荐）
```bash
./start_local.sh
```

### 方式 2：直接运行 Python 脚本
```bash
python run_local.py
```

### 方式 3：手动启动
```bash
conda activate insightface-rest-py310
export NUMBA_CACHE_DIR=/tmp/numba_cache
export NUMBA_DISABLE_JIT=0
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080
```

## ⚠️ 需要避免的配置

❌ **不要使用以下命令**（会导致 pickle 错误）：

```bash
# ❌ --reload 导致 multiprocessing 问题
uvicorn if_rest.api.main:app --reload

# ❌ Gunicorn 多 worker 会触发序列化
gunicorn -w 4 -k uvicorn.workers.UvicornWorker if_rest.api.main:app

# ❌ Python 3.8 的类型提示问题
# （已通过升级到 3.10 解决）
```

## ✓ 性能优化

如果需要更好的性能且不想使用 --reload：

### 编辑代码时自动重启（使用 watchdog）
```bash
pip install watchdog
watchmedo auto-restart -d . -p '*.py' -- uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080
```

### 使用 Supervisor 管理进程
创建 `/etc/supervisor/conf.d/insightface.conf`：
```ini
[program:insightface]
command=/Users/habi/InsightFace-REST/start_local.sh
autostart=true
autorestart=true
startsecs=10
```

## 📝 测试 API

修复后测试 API：

```bash
# 1. 启动服务
./start_local.sh

# 2. 在新终端中测试
curl -X POST http://localhost:18080/extract \
  -H "Content-Type: application/json" \
  -d '{
    "data": ["base64_image_data"],
    "det_name": "scrfd_10g_gnkps",
    "rec_name": "glintr100"
  }'

# 3. 或访问 API 文档
open http://localhost:18080/docs
```

## 📊 故障排除清单

- [ ] 使用的是 Python 3.10+（不是 3.8）
- [ ] 没有使用 `--reload` 参数
- [ ] 环境变量已正确设置：
  ```bash
  echo $NUMBA_CACHE_DIR  # 应输出 /tmp/numba_cache
  echo $NUMBA_DISABLE_JIT # 应输出 0
  ```
- [ ] 使用 `./start_local.sh` 或 `python run_local.py` 启动
- [ ] 模型文件已下载到 `./models/onnx/` 目录
- [ ] 虚拟环境已激活：
  ```bash
  conda activate insightface-rest-py310
  ```

## 🎯 如果仍然出现错误

### 步骤 1：清理 Numba 缓存
```bash
rm -rf /tmp/numba_cache
mkdir -p /tmp/numba_cache
```

### 步骤 2：重新安装依赖
```bash
pip install --upgrade numba
pip install --upgrade onnxruntime
```

### 步骤 3：完全重启虚拟环境
```bash
# 删除现有环境
conda remove -n insightface-rest-py310 --all

# 重建环境
conda create -n insightface-rest-py310 python=3.10 -y
conda activate insightface-rest-py310
pip install -r requirements.txt
```

### 步骤 4：检查日志中的详细错误
运行时观察错误信息，查找具体是哪个函数导致问题。

## 📚 相关文档

- [Python Pickle 官方文档](https://docs.python.org/3/library/pickle.html)
- [Numba 并行编程](https://numba.pydata.org/numba-doc/latest/user/parallel.html)
- [Uvicorn 文档](https://www.uvicorn.org/)

---

**状态**: ✅ 已修复  
**建议**: 使用提供的启动脚本，不要手动修改启动命令  
**最后更新**: 2025-11-14
