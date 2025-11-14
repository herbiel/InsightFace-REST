#!/bin/bash
set -e

# 进入项目根目录
cd "$(dirname "$0")"

# 设置 Numba 环境变量以避免 multiprocessing 兼容性问题
export NUMBA_CACHE_DIR=/tmp/numba_cache
export NUMBA_DISABLE_JIT=0

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    echo -e "${BLUE}激活虚拟环境...${NC}"
    source venv/bin/activate
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  InsightFace-REST - 本地启动脚本            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""

# 检查依赖
echo -e "${BLUE}✓ 检查依赖...${NC}"
python -c "import uvicorn; import fastapi; import onnxruntime" 2>/dev/null || {
    echo -e "${BLUE}安装缺失的依赖...${NC}"
    pip install -r requirements.txt -q -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
}

# 验证配置
echo -e "${BLUE}✓ 验证配置...${NC}"
python -c "from if_rest.core.configs import config; print(f'  模型目录: {config.models_dir}'); print(f'  已加载模型数: {len(config.models)}')"

echo ""
echo -e "${GREEN}✓ 配置完成！${NC}"
echo ""
echo -e "${BLUE}启动 FastAPI 服务...${NC}"
echo -e "${GREEN}📍 API 文档: http://localhost:18080/docs${NC}"
echo -e "${GREEN}🔗 API 地址: http://localhost:18080${NC}"
echo -e "${GREEN}📊 OpenAPI: http://localhost:18080/openapi.json${NC}"
echo ""
echo -e "${BLUE}按 Ctrl+C 停止服务${NC}"
echo ""

# 启动服务（开发模式，不使用 reload 以避免 multiprocessing 问题）
uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080

# 可选：生产模式（多 worker，但需要正确处理 multiprocessing）
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker --keep-alive 60 --timeout 60 if_rest.api.main:app -b 0.0.0.0:18080
