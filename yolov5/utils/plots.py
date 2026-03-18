"""
Plotting utilities for training visualization
绘制训练曲线、混淆矩阵、PR曲线等
"""

import os
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional
import seaborn as sns


class TrainingPlotter:
    """训练过程可视化器"""

    def __init__(self, save_dir: Path):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.history = {
            'epoch': [],
            'train_loss': [],
            'val_loss': [],
            'precision': [],
            'recall': [],
            'mAP@0.5': [],
            'f1': []
        }

    def update(self, epoch: int, metrics: Dict[str, float]):
        self.history['epoch'].append(epoch)
        for key in self.history.keys():
            if key != 'epoch':
                self.history[key].append(metrics.get(key, None))

    def _get_valid_data(self, key: str):
        epochs, values = [], []
        for e, v in zip(self.history['epoch'], self.history[key]):
            if v is not None:
                epochs.append(e)
                values.append(v)
        return epochs, values

    def plot_training_curves(self):
        if not self.history['epoch']:
            return

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle('YOLOv5 Training Metrics', fontsize=16, fontweight='bold')

        # Loss
        ax = axes[0, 0]
        ep, vals = self._get_valid_data('train_loss')
        if vals:
            ax.plot(ep, vals, 'b-', label='Train Loss', linewidth=2)
        ep, vals = self._get_valid_data('val_loss')
        if vals:
            ax.plot(ep, vals, 'r-', label='Val Loss', linewidth=2)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Loss')
        ax.set_title('Loss Curve')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Precision & Recall
        ax = axes[0, 1]
        ep, vals = self._get_valid_data('precision')
        if vals:
            ax.plot(ep, vals, 'g-', label='Precision', linewidth=2)
        ep, vals = self._get_valid_data('recall')
        if vals:
            ax.plot(ep, vals, 'b-', label='Recall', linewidth=2)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Score')
        ax.set_title('Precision & Recall')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])

        # mAP@0.5
        ax = axes[1, 0]
        ep, vals = self._get_valid_data('mAP@0.5')
        if vals:
            ax.plot(ep, vals, 'purple', label='mAP@0.5', linewidth=2)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('mAP')
        ax.set_title('mAP@0.5')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])

        # F1
        ax = axes[1, 1]
        ep, vals = self._get_valid_data('f1')
        if vals:
            ax.plot(ep, vals, 'red', label='F1 Score', linewidth=2)
        ax.set_xlabel('Epoch')
        ax.set_ylabel('F1 Score')
        ax.set_title('F1 Score')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])

        plt.tight_layout()
        save_path = self.save_dir / 'training_curves.png'
        plt.savefig(save_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'Training curves saved to {save_path}')

    def plot_confusion_matrix(self, cm_matrix: np.ndarray, class_names: List[str]):
        nc = min(20, len(class_names))
        cm = cm_matrix[:nc, :nc]
        names = class_names[:nc]

        fig, ax = plt.subplots(figsize=(12, 10))
        cm_norm = cm.astype('float') / (cm.sum(axis=1, keepdims=True) + 1e-16)
        sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
                    xticklabels=names, yticklabels=names, square=True, ax=ax)
        ax.set_xlabel('Predicted', fontsize=12, fontweight='bold')
        ax.set_ylabel('True', fontsize=12, fontweight='bold')
        ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')

        plt.tight_layout()
        save_path = self.save_dir / 'confusion_matrix.png'
        plt.savefig(save_path, dpi=200, bbox_inches='tight')
        plt.close()
        print(f'Confusion matrix saved to {save_path}')

    def save_metrics_csv(self):
        import pandas as pd
        df = pd.DataFrame(self.history)
        save_path = self.save_dir / 'metrics.csv'
        df.to_csv(save_path, index=False)
        print(f'Metrics saved to {save_path}')


def _get_color_palette(n_colors: int = 80):
    colors = [
        (255, 56, 56), (255, 157, 151), (255, 112, 31), (255, 178, 29),
        (207, 210, 49), (72, 249, 10), (146, 204, 23), (61, 219, 134),
        (26, 147, 52), (0, 212, 187), (44, 153, 168), (0, 194, 255),
        (52, 69, 147), (100, 115, 255), (0, 24, 236), (132, 56, 255),
        (82, 0, 133), (203, 56, 255), (255, 149, 200), (255, 55, 199),
    ]
    while len(colors) < n_colors:
        colors = colors + colors
    return colors[:n_colors]


def plot_detection_samples(
    images: List[np.ndarray],
    predictions: List[List[Dict]],
    targets: List[np.ndarray],
    class_names: List[str],
    save_dir: Path,
    max_images: int = 16
):
    """绘制检测样本"""
    n_images = min(len(images), max_images)
    n_cols = 4
    n_rows = (n_images + n_cols - 1) // n_cols
    colors = _get_color_palette(len(class_names))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)

    for idx in range(n_images):
        row, col = idx // n_cols, idx % n_cols
        ax = axes[row, col]
        img = images[idx].copy()
        if img.dtype == np.float32 or img.dtype == np.float64:
            img = (img * 255).astype(np.uint8)
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.shape[0] == 3:
            img = img.transpose(1, 2, 0)
        img = np.ascontiguousarray(img)

        # GT
        if idx < len(targets) and len(targets[idx]) > 0:
            for gt in targets[idx]:
                cls_id = int(gt[0])
                x1, y1, x2, y2 = gt[1:5]
                h, w = img.shape[:2]
                if x2 <= 1.0:
                    cx, cy, bw, bh = x1, y1, x2, y2
                    x1 = int((cx - bw / 2) * w)
                    y1 = int((cy - bh / 2) * h)
                    x2 = int((cx + bw / 2) * w)
                    y2 = int((cy + bh / 2) * h)
                else:
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                color = colors[cls_id % len(colors)]
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                label = class_names[cls_id] if cls_id < len(class_names) else f'cls{cls_id}'
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(img, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
                cv2.putText(img, label, (x1 + 2, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Predictions
        if idx < len(predictions):
            for pred in predictions[idx]:
                cls_id = pred['class_id']
                conf = pred['confidence']
                x1, y1, x2, y2 = map(int, pred['bbox'])
                color = colors[cls_id % len(colors)]
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                label = f"{class_names[cls_id] if cls_id < len(class_names) else f'cls{cls_id}'} {conf:.2f}"
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                cv2.rectangle(img, (x1, y2), (x1 + tw + 4, y2 + th + 6), color, -1)
                cv2.putText(img, label, (x1 + 2, y2 + th + 2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        ax.imshow(img)
        ax.axis('off')
        ax.set_title(f'Image {idx}', fontsize=10)

    for idx in range(n_images, n_rows * n_cols):
        axes[idx // n_cols, idx % n_cols].axis('off')

    plt.tight_layout()
    save_path = save_dir / 'val_batch_predictions.jpg'
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f'Detection samples saved to {save_path}')


def plot_labels_distribution(targets: List[np.ndarray], class_names: List[str], save_dir: Path):
    """绘制标签分布"""
    class_counts = {}
    box_sizes = []

    for target in targets:
        if len(target) == 0:
            continue
        for obj in target:
            cls_id = int(obj[0])
            class_counts[cls_id] = class_counts.get(cls_id, 0) + 1
            if len(obj) >= 5:
                box_sizes.append(obj[3] * obj[4])

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    ax = axes[0]
    if class_counts:
        classes = sorted(class_counts.keys())[:20]
        counts = [class_counts[c] for c in classes]
        labels = [class_names[c] if c < len(class_names) else f'cls{c}' for c in classes]
        ax.bar(range(len(classes)), counts, color='steelblue')
        ax.set_xticks(range(len(classes)))
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.set_xlabel('Class')
        ax.set_ylabel('Count')
        ax.set_title('Class Distribution')
        ax.grid(True, alpha=0.3, axis='y')

    ax = axes[1]
    if box_sizes:
        ax.hist(box_sizes, bins=50, color='coral', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Box Area (normalized)')
        ax.set_ylabel('Count')
        ax.set_title('Bounding Box Size Distribution')
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    save_path = save_dir / 'labels_distribution.png'
    plt.savefig(save_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f'Labels distribution saved to {save_path}')
