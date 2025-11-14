#!/usr/bin/env python3
"""
InsightFace-REST 本地启动脚本（multiprocessing 安全版本）
避免 Numba JIT 编译函数序列化问题
"""

import os
import sys
import subprocess

# 设置 Numba 环境变量以避免 pickle 问题
os.environ['NUMBA_CACHE_DIR'] = '/tmp/numba_cache'
os.environ['NUMBA_DISABLE_JIT'] = '0'  # 保持 JIT 启用以获得性能

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """启动 FastAPI 应用"""
    
    print("\n" + "="*60)
    print("  InsightFace-REST - 本地启动 (multiprocessing 安全)")
    print("="*60 + "\n")
    
    # 验证虚拟环境
    if 'insightface-rest-py310' not in os.environ.get('CONDA_DEFAULT_ENV', ''):
        print("⚠️  警告: 未激活 insightface-rest-py310 虚拟环境")
        print("   请运行: conda activate insightface-rest-py310\n")
    
    # 检查依赖
    try:
        from if_rest.core.configs import config
        print(f"✓ 模型目录: {config.models_dir}")
        print(f"✓ 已加载模型数: {len(config.models)}\n")
    except Exception as e:
        print(f"❌ 配置检查失败: {e}\n")
        return 1
    
    print("✓ 配置完成！\n")
    print("启动 FastAPI 服务...")
    print("📍 API 文档: http://localhost:18080/docs")
    print("🔗 API 地址: http://localhost:18080")
    print("📊 OpenAPI: http://localhost:18080/openapi.json")
    print("\n按 Ctrl+C 停止服务\n")
    
    # 启动 Uvicorn（不使用 reload 以避免 multiprocessing 问题）
    cmd = [
        'uvicorn',
        'if_rest.api.main:app',
        '--host', '0.0.0.0',
        '--port', '18080',
        # 不添加 --reload 因为它会导致 Numba 函数序列化问题
    ]
    
    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print("\n\n正在关闭服务...")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
