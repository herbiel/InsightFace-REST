#!/bin/bash

# 彩色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║     InsightFace-REST 本地运行 - 配置完成！                ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${BLUE}✓ 已完成的配置：${NC}"
echo "  1. ✅ 创建 Python 3.10 虚拟环境"
echo "  2. ✅ 安装所有依赖包"
echo "  3. ✅ 修复 Python 3.8/3.9 兼容性问题"
echo "  4. ✅ 创建模型下载工具"
echo "  5. ✅ 创建启动脚本"

echo ""
echo -e "${BLUE}📋 虚拟环境信息：${NC}"
echo "  环境名称: ${YELLOW}insightface-rest-py310${NC}"
echo "  Python 版本: ${YELLOW}3.10${NC}"
echo "  激活命令: ${YELLOW}conda activate insightface-rest-py310${NC}"

echo ""
echo -e "${BLUE}🚀 快速启动 (3 个命令)：${NC}"
echo ""
echo "  # 1. 激活虚拟环境"
echo -e "  ${YELLOW}conda activate insightface-rest-py310${NC}"
echo ""
echo "  # 2. 下载模型文件（首次运行）"
echo -e "  ${YELLOW}python download_models.py${NC}"
echo ""
echo "  # 3. 启动 API 服务"
echo -e "  ${YELLOW}./start_local.sh${NC}"
echo ""
echo "  或直接运行:"
echo -e "  ${YELLOW}uvicorn if_rest.api.main:app --host 0.0.0.0 --port 18080${NC}"

echo ""
echo -e "${BLUE}🌐 API 访问地址：${NC}"
echo "  • API 文档 (Swagger): ${YELLOW}http://localhost:18080/docs${NC}"
echo "  • ReDoc 文档: ${YELLOW}http://localhost:18080/redoc${NC}"
echo "  • OpenAPI 规范: ${YELLOW}http://localhost:18080/openapi.json${NC}"

echo ""
echo -e "${BLUE}📥 模型下载选项：${NC}"
echo ""
echo "  # 下载默认模型 (scrfd_10g_gnkps + glintr100) - 推荐"
echo -e "  ${YELLOW}python download_models.py${NC}"
echo ""
echo "  # 下载轻量级模型 (更快但精度稍低)"
echo -e "  ${YELLOW}python download_models.py --models scrfd_500m_gnkps w600k_mbf${NC}"
echo ""
echo "  # 下载特定模型"
echo -e "  ${YELLOW}python download_models.py --det scrfd_10g_gnkps${NC}"
echo -e "  ${YELLOW}python download_models.py --rec glintr100${NC}"
echo ""
echo "  # 下载所有模型"
echo -e "  ${YELLOW}python download_models.py --all${NC}"

echo ""
echo -e "${BLUE}📚 详细文档：${NC}"
echo "  • 快速启动指南: ${YELLOW}QUICKSTART_LOCAL.md${NC}"
echo "  • 完整配置文档: ${YELLOW}LOCAL_SETUP.md${NC}"

echo ""
echo -e "${BLUE}⚠️  注意事项：${NC}"
echo "  • 模型文件较大 (100MB-500MB)，首次下载需要耐心等待"
echo "  • 如果 Google Drive 无法访问，可以手动下载或使用代理"
echo "  • 第一次启动时，API 会加载模型到内存，可能需要几秒钟"
echo "  • CPU 模式下推理速度较慢，建议使用 GPU（可选）"

echo ""
echo -e "${GREEN}✅ 配置完成！现在就可以启动服务了！${NC}"
echo ""
