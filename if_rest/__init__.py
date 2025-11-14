"""
InsightFace-REST package initialization
"""
import os

# 设置 Numba 环境变量以避免 multiprocessing 兼容性问题
# 这必须在任何 numba 代码被导入之前设置
os.environ.setdefault('NUMBA_CACHE_DIR', '/tmp/numba_cache')
os.environ.setdefault('NUMBA_DISABLE_JIT', '0')

__version__ = '0.9.5.0'
