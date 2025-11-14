#!/usr/bin/env python3
"""
下载 InsightFace-REST 所需的模型文件

使用方法:
    python download_models.py              # 下载默认模型
    python download_models.py --all        # 下载所有模型
    python download_models.py --det scrfd_10g_gnkps  # 下载特定检测模型
"""

import json
import os
import sys
from pathlib import Path
from urllib.request import urlopen
import gdown

# 模型配置文件路径
MODELS_CONFIG = Path(__file__).parent / 'models' / 'models.json'

# Google Drive 模型映射（ID -> 模型名称）
GOOGLE_DRIVE_MODELS = {
    # 检测模型 (Detection)
    'scrfd_10g_gnkps': '14BuXR6L73w1mwKXHPIcZlc9LYaid4Evl',
    'scrfd_2.5g_gnkps': '1_LeETpKhWL4sRPvLZEvka-bGNMN4tMOU',
    'scrfd_500m_gnkps': '19CeBV03a3DEhZeas4olZn7GgiUESDu0L',
    'retinaface_r50_v1': '1peUaq0TtNBhoXUbMqsCyQdL7t5JuhHMH',
    
    # 识别模型 (Recognition)
    'glintr100': '1TR_ImGvuY7Dt22a9BOAUAlHasFfkrJp-',
    'w600k_r50': '1_3WcTE64Mlt_12PZHNWdhVCRpoPiblwq',
    'arcface_r100_v1': '1sj170K3rbo5iOdjvjHw-hKWvXgH4dld3',
}

# 默认下载的模型组合
DEFAULT_MODELS = ['scrfd_10g_gnkps', 'glintr100']

def load_models_config():
    """加载模型配置"""
    if not MODELS_CONFIG.exists():
        print(f"❌ 错误: 找不到 {MODELS_CONFIG}")
        sys.exit(1)
    
    with open(MODELS_CONFIG) as f:
        return json.load(f)

def get_model_info(model_name, models_config):
    """获取模型信息"""
    if model_name not in models_config:
        print(f"❌ 错误: 未知模型 '{model_name}'")
        return None
    
    model_info = models_config[model_name]
    return model_info

def download_model(model_name, models_dir='models'):
    """下载单个模型"""
    models_config = load_models_config()
    model_info = get_model_info(model_name, models_config)
    
    if not model_info:
        return False
    
    # 确定模型类型和输出路径
    model_type = 'onnx'  # 默认 ONNX 格式
    model_dir = Path(models_dir) / model_type / model_name
    model_dir.mkdir(parents=True, exist_ok=True)
    
    model_file = model_dir / f"{model_name}.onnx"
    
    if model_file.exists():
        print(f"✓ 模型已存在: {model_file}")
        return True
    
    # 获取下载链接
    download_link = model_info.get('link')
    dl_type = model_info.get('dl_type', 'google')
    
    if not download_link:
        print(f"⚠️  警告: 模型 '{model_name}' 没有下载链接")
        return False
    
    print(f"\n📥 下载模型: {model_name}")
    print(f"   保存位置: {model_file}")
    
    try:
        if dl_type == 'google':
            # Google Drive 下载
            print(f"   来源: Google Drive (ID: {download_link})")
            gdown.download(f'https://drive.google.com/uc?id={download_link}', 
                          str(model_file), quiet=False)
        else:
            # 直接 URL 下载 (如 CenterFace)
            print(f"   来源: 直接 URL")
            urlopen(download_link)
            # 此处需要实现实际下载逻辑
            print(f"⚠️  URL 下载需要手动实现")
            return False
        
        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024*1024)
            print(f"✅ 下载完成! 文件大小: {size_mb:.1f} MB")
            return True
        else:
            print(f"❌ 下载失败: 文件未保存")
            return False
            
    except Exception as e:
        print(f"❌ 下载出错: {e}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='下载 InsightFace-REST 模型')
    parser.add_argument('--all', action='store_true', help='下载所有模型')
    parser.add_argument('--det', help='下载特定检测模型')
    parser.add_argument('--rec', help='下载特定识别模型')
    parser.add_argument('--models', nargs='+', help='下载指定的模型列表')
    parser.add_argument('--models-dir', default='models', help='模型保存目录')
    
    args = parser.parse_args()
    
    # 确定要下载的模型列表
    models_to_download = []
    
    if args.all:
        models_config = load_models_config()
        models_to_download = list(GOOGLE_DRIVE_MODELS.keys())
    elif args.models:
        models_to_download = args.models
    elif args.det or args.rec:
        if args.det:
            models_to_download.append(args.det)
        if args.rec:
            models_to_download.append(args.rec)
    else:
        # 默认模型
        models_to_download = DEFAULT_MODELS
    
    print(f"\n{'='*50}")
    print(f"  InsightFace-REST 模型下载工具")
    print(f"{'='*50}\n")
    print(f"待下载模型 ({len(models_to_download)}):")
    for model in models_to_download:
        print(f"  • {model}")
    print()
    
    # 下载模型
    success_count = 0
    failed_models = []
    
    for model_name in models_to_download:
        if download_model(model_name, args.models_dir):
            success_count += 1
        else:
            failed_models.append(model_name)
    
    # 总结
    print(f"\n{'='*50}")
    print(f"  下载完成")
    print(f"{'='*50}")
    print(f"✅ 成功: {success_count}/{len(models_to_download)}")
    
    if failed_models:
        print(f"❌ 失败: {', '.join(failed_models)}")
        print(f"\n💡 提示: 模型可能需要从 Google Drive 手动下载")
        print(f"         模型配置见: models/models.json")
    
    return 0 if not failed_models else 1

if __name__ == '__main__':
    sys.exit(main())
