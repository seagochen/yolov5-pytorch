"""
YOLOv5 Detection Script
支持单张图像、批量图像和视频检测
"""

import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import torch
import cv2
import yaml
import numpy as np
from tqdm import tqdm

from yolov5.models import create_yolov5
from yolov5.utils import nms, colorstr, increment_path


def parse_args():
    parser = argparse.ArgumentParser(description='YOLOv5 Detection')

    parser.add_argument('--weights', type=str, required=True, help='Model weights path')
    parser.add_argument('--source', type=str, required=True, help='Source: image/folder/video')
    parser.add_argument('--data', type=str, default='data/coco.yaml', help='Dataset YAML')
    parser.add_argument('--img-size', type=int, default=640, help='Inference size')
    parser.add_argument('--conf-thres', type=float, default=0.5, help='Confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='NMS IoU threshold')
    parser.add_argument('--device', type=str, default='0', help='CUDA device or cpu')
    parser.add_argument('--project', type=str, default='runs/detect', help='Save directory')
    parser.add_argument('--name', type=str, default='exp', help='Experiment name')
    parser.add_argument('--save-img', action='store_true', help='Save results')
    parser.add_argument('--view-img', action='store_true', help='Display results')
    parser.add_argument('--exist-ok', action='store_true', help='Allow existing dir')

    return parser.parse_args()


def load_model(weights_path, device, num_classes=None):
    """加载模型"""
    print(colorstr('bright_green', f'\nLoading model from {weights_path}'))

    ckpt = torch.load(weights_path, map_location=device, weights_only=False)

    if 'model' in ckpt:
        state_dict = ckpt['model']
    elif 'model_state_dict' in ckpt:
        state_dict = ckpt['model_state_dict']
    else:
        state_dict = ckpt

    # 获取模型变体和类别数
    variant = ckpt.get('variant', 's')
    if num_classes is None:
        num_classes = ckpt.get('num_classes', None)

    if num_classes is None:
        # 从检测头推断类别数
        for key in state_dict:
            if 'detect.heads.0.weight' in key:
                out_channels = state_dict[key].shape[0]
                num_classes = out_channels // 3 - 5  # 3 anchors per scale
                break
        if num_classes is None:
            num_classes = 80
        print(colorstr('bright_yellow', f'Inferred num_classes={num_classes}'))

    model = create_yolov5(num_classes=num_classes, img_size=640, variant=variant)
    model.load_state_dict(state_dict)
    model = model.to(device)
    model.eval()

    print(colorstr('bright_green', 'Model loaded successfully'))
    return model, num_classes


def load_class_names(yaml_path, num_classes=80):
    if not os.path.exists(yaml_path):
        return [f'class_{i}' for i in range(num_classes)]
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    return config.get('names', [f'class_{i}' for i in range(num_classes)])


def draw_boxes(img, detections, class_names):
    """在图像上绘制检测框"""
    img = img.copy()
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 0, 0), (0, 128, 0), (0, 0, 128)
    ]

    for det in detections:
        class_id = det['class_id']
        conf = det['confidence']
        x1, y1, x2, y2 = map(int, det['bbox'])
        color = colors[class_id % len(colors)]

        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        class_name = class_names[class_id] if class_id < len(class_names) else f'cls{class_id}'
        label = f'{class_name} {conf:.2f}'
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (x1, y1 - th - 5), (x1 + tw, y1), color, -1)
        cv2.putText(img, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return img


def detect_image(model, img_path, device, conf_thres, iou_thres, class_names,
                 save_dir=None, view=False):
    """检测单张图像"""
    img = cv2.imread(str(img_path))
    if img is None:
        print(f'Failed to load: {img_path}')
        return []

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (640, 640))

    img_tensor = torch.from_numpy(img_resized).permute(2, 0, 1).float() / 255.0
    img_tensor = img_tensor.unsqueeze(0).to(device)

    with torch.no_grad():
        predictions = model.predict(img_tensor, conf_threshold=conf_thres, device=device)

    detections = predictions[0]
    detections = nms(detections, iou_threshold=iou_thres)

    print(f'{img_path.name}: {len(detections)} objects')

    if save_dir or view:
        h, w = img.shape[:2]
        scale_x, scale_y = w / 640, h / 640

        scaled_dets = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            scaled_dets.append({
                'class_id': det['class_id'],
                'confidence': det['confidence'],
                'bbox': (x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y)
            })

        result = draw_boxes(img, scaled_dets, class_names)

        if save_dir:
            cv2.imwrite(str(save_dir / img_path.name), result)
        if view:
            cv2.imshow('Detection', result)
            cv2.waitKey(0)

    return detections


def main():
    args = parse_args()
    device = torch.device('cuda:0' if torch.cuda.is_available() and args.device != 'cpu' else 'cpu')

    save_dir = Path(increment_path(Path(args.project) / args.name, exist_ok=args.exist_ok))
    if args.save_img:
        save_dir.mkdir(parents=True, exist_ok=True)
    else:
        save_dir = None

    model, num_classes = load_model(args.weights, device)
    class_names = load_class_names(args.data, num_classes)

    source = Path(args.source)

    if source.is_file():
        detect_image(model, source, device, args.conf_thres, args.iou_thres,
                     class_names, save_dir, args.view_img)
    elif source.is_dir():
        img_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
            img_files.extend(source.glob(ext))

        print(colorstr('bright_cyan', f'\nProcessing {len(img_files)} images'))
        for img_path in tqdm(img_files):
            detect_image(model, img_path, device, args.conf_thres, args.iou_thres,
                         class_names, save_dir, False)
    else:
        print(f'Invalid source: {source}')

    if args.save_img:
        print(colorstr('bright_green', f'\nResults saved to {save_dir}'))
    if args.view_img:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
