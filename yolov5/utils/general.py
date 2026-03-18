"""
General utility functions
通用工具函数
"""

import torch
import torchvision
import numpy as np
from typing import List, Dict, Tuple
from pathlib import Path


def nms(
    detections: List[Dict],
    iou_threshold: float = 0.5
) -> List[Dict]:
    """
    非极大值抑制 (NMS) - 使用 torchvision.ops.nms

    Args:
        detections: 检测结果列表，每个dict包含 'class_id', 'confidence', 'bbox'
        iou_threshold: IoU阈值

    Returns:
        filtered: NMS后的检测结果
    """
    if len(detections) == 0:
        return []

    boxes = []
    scores = []
    class_ids = []

    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        boxes.append([x1, y1, x2, y2])
        scores.append(det['confidence'])
        class_ids.append(det['class_id'])

    boxes_t = torch.tensor(boxes, device='cpu', dtype=torch.float32)
    scores_t = torch.tensor(scores, device='cpu', dtype=torch.float32)
    class_ids_t = torch.tensor(class_ids, device='cpu', dtype=torch.int64)

    # 按类别分别做 NMS (坐标偏移技巧)
    max_coordinate = boxes_t.max() + 5000
    offsets = class_ids_t.float() * max_coordinate
    boxes_for_nms = boxes_t + offsets[:, None]

    keep_indices = torchvision.ops.nms(boxes_for_nms, scores_t, iou_threshold)
    filtered = [detections[idx] for idx in keep_indices.numpy()]

    return filtered


def box_iou(box1: Tuple, box2: Tuple) -> float:
    """计算两个框的IoU"""
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    x1_inter = max(x1_1, x1_2)
    y1_inter = max(y1_1, y1_2)
    x2_inter = min(x2_1, x2_2)
    y2_inter = min(y2_1, y2_2)

    inter_area = max(0, x2_inter - x1_inter) * max(0, y2_inter - y1_inter)
    box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
    box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
    union_area = box1_area + box2_area - inter_area

    return inter_area / (union_area + 1e-16)


def check_img_size(img_size: int, stride: int = 32) -> int:
    """验证 img_size 是 stride 的倍数"""
    new_size = max(stride, (img_size // stride) * stride)
    if new_size != img_size:
        print(f'Warning: img_size {img_size} is not a multiple of stride {stride}. '
              f'Using {new_size} instead.')
    return new_size


def init_seeds(seed: int = 0):
    """初始化随机种子"""
    import random
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def check_file(file: str) -> Path:
    """验证文件存在"""
    file = Path(file)
    if not file.exists():
        raise FileNotFoundError(f'File not found: {file}')
    return file


def increment_path(path: Path, exist_ok: bool = False, sep: str = '_') -> Path:
    """自动增加路径后缀以避免覆盖"""
    path = Path(path)
    if not path.exists() or exist_ok:
        return path

    path, suffix = (path.with_suffix(''), path.suffix) if path.is_file() else (path, '')

    for n in range(2, 100):
        p = f'{path}{sep}{n}{suffix}'
        if not Path(p).exists():
            return Path(p)

    import time
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    return Path(f'{path}{sep}{timestamp}{suffix}')


def colorstr(*args):
    """彩色终端字符串"""
    *args, string = args if len(args) > 1 else ('blue', 'bold', args[0])
    colors = {
        'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m',
        'yellow': '\033[33m', 'blue': '\033[34m', 'magenta': '\033[35m',
        'cyan': '\033[36m', 'white': '\033[37m',
        'bright_black': '\033[90m', 'bright_red': '\033[91m',
        'bright_green': '\033[92m', 'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m', 'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m', 'bright_white': '\033[97m',
        'end': '\033[0m', 'bold': '\033[1m', 'underline': '\033[4m'
    }
    return ''.join(colors.get(x, '') for x in args) + f'{string}' + colors['end']
