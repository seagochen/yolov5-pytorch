"""
Dataset classes with full Ultralytics format compatibility
完全兼容 Ultralytics YAML+TXT 格式, 支持 YOLOv5 多尺度检测
"""

import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import yaml


class COCODetectionDataset(Dataset):
    """
    COCO Detection Dataset - 完全兼容 Ultralytics 格式

    YOLOv5 版本与 YOLOv2 的区别:
    - targets 格式改为 (N, 6): [batch_idx, class_id, cx, cy, w, h]
      这样可以在 collate_fn 中方便地合并多张图的 targets
    - 不再预编码为 anchor-grid 格式 (由 loss 函数负责匹配)
    - 支持更丰富的数据增强 (mosaic, mixup 等可扩展)
    """

    def __init__(
        self,
        yaml_path: str,
        split: str = 'train',
        img_size: int = 640,
        augment: bool = False,
        cache_images: bool = False
    ):
        super().__init__()

        self.split = split
        self.img_size = img_size
        self.augment = augment
        self.cache_images = cache_images

        # 加载配置
        self.config = self._load_yaml(yaml_path)

        # 解析路径
        self.dataset_root = self._parse_dataset_root(yaml_path)
        self.img_dir, self.label_dir = self._parse_split_paths(split)

        # 类别信息
        self.num_classes = self.config['nc']
        self.class_names = self.config['names']

        # 扫描图像文件
        self.img_files = self._scan_images()

        # 图像缓存
        self.imgs = [None] * len(self.img_files) if cache_images else None

        self._print_stats()

    def _load_yaml(self, yaml_path: str) -> Dict:
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML config not found: {yaml_path}")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        for field in ['nc', 'names']:
            if field not in config:
                raise ValueError(f"Missing required field in YAML: {field}")
        return config

    def _parse_dataset_root(self, yaml_path: str) -> Path:
        yaml_path = Path(yaml_path)
        if 'path' in self.config:
            root = Path(self.config['path'])
            if root.is_absolute() and root.exists():
                return root
        return yaml_path.parent

    def _parse_split_paths(self, split: str) -> Tuple[Path, Path]:
        img_subpath = self.config.get(split, f'images/{split}')

        # Roboflow 格式兼容
        if str(img_subpath).startswith('../'):
            img_subpath_clean = str(img_subpath)[3:]
            img_dir = self.dataset_root / img_subpath_clean
        else:
            img_dir = self.dataset_root / img_subpath

        label_subpath = img_subpath.replace('images', 'labels')
        if str(label_subpath).startswith('../'):
            label_subpath_clean = str(label_subpath)[3:]
            label_dir = self.dataset_root / label_subpath_clean
        else:
            label_dir = self.dataset_root / label_subpath

        if not img_dir.exists():
            print(f"Warning: Image directory not found: {img_dir}")
        if not label_dir.exists():
            print(f"Warning: Label directory not found: {label_dir}")

        return img_dir, label_dir

    def _scan_images(self) -> List[Path]:
        if not self.img_dir.exists():
            return []
        img_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        img_files = []
        for ext in img_extensions:
            img_files.extend(self.img_dir.glob(f'*{ext}'))
            img_files.extend(self.img_dir.glob(f'*{ext.upper()}'))
        return sorted(img_files)

    def _print_stats(self):
        print(f"\n{'='*60}")
        print(f"Dataset: {self.split}")
        print(f"{'='*60}")
        print(f"Root: {self.dataset_root}")
        print(f"Images: {self.img_dir}")
        print(f"Labels: {self.label_dir}")
        print(f"Number of images: {len(self.img_files)}")
        print(f"Number of classes: {self.num_classes}")
        print(f"Image size: {self.img_size}")
        print(f"Augmentation: {self.augment}")
        print(f"{'='*60}\n")

    def __len__(self) -> int:
        return len(self.img_files)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        获取一个样本

        Returns:
            image: (3, img_size, img_size) Tensor
            labels: (N, 6) Tensor [batch_idx(=0), class_id, cx, cy, w, h] (归一化)
        """
        img = self._load_image(index)
        labels = self._load_labels(index)

        if self.augment:
            img, labels = self._apply_augmentations(img, labels)

        # Resize
        img = cv2.resize(img, (self.img_size, self.img_size))

        # 转为 Tensor
        img = self._img_to_tensor(img)

        # 标签格式: (N, 6) [batch_idx, class_id, cx, cy, w, h]
        if len(labels) > 0:
            nl = len(labels)
            target = torch.zeros(nl, 6, dtype=torch.float32)
            labels_arr = np.array(labels, dtype=np.float32)
            target[:, 1] = torch.from_numpy(labels_arr[:, 0])   # class_id
            target[:, 2:6] = torch.from_numpy(labels_arr[:, 1:5])  # cx, cy, w, h
            # batch_idx (target[:, 0]) 在 collate_fn 中设置
        else:
            target = torch.zeros(0, 6, dtype=torch.float32)

        return img, target

    def _load_image(self, index: int) -> np.ndarray:
        if self.imgs is not None and self.imgs[index] is not None:
            return self.imgs[index].copy()
        img_path = self.img_files[index]
        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Warning: Failed to load image: {img_path}")
            img = np.zeros((self.img_size, self.img_size, 3), dtype=np.uint8)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if self.imgs is not None:
            self.imgs[index] = img.copy()
        return img

    def _load_labels(self, index: int) -> List[Tuple]:
        """返回 List of (class_id, cx, cy, w, h)"""
        img_path = self.img_files[index]
        label_path = self.label_dir / (img_path.stem + '.txt')
        if not label_path.exists():
            return []
        labels = []
        with open(label_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue
                try:
                    class_id = int(parts[0])
                    cx, cy, w, h = map(float, parts[1:5])
                    if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 < w <= 1 and 0 < h <= 1):
                        continue
                    if class_id < 0 or class_id >= self.num_classes:
                        continue
                    labels.append((class_id, cx, cy, w, h))
                except (ValueError, IndexError):
                    continue
        return labels

    def _img_to_tensor(self, img: np.ndarray) -> torch.Tensor:
        img = img.transpose(2, 0, 1).astype(np.float32) / 255.0
        return torch.from_numpy(img)

    def _apply_augmentations(
        self,
        img: np.ndarray,
        labels: List[Tuple]
    ) -> Tuple[np.ndarray, List[Tuple]]:
        """数据增强"""
        # HSV 增强
        if np.random.rand() > 0.5:
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + np.random.uniform(-10, 10)) % 180
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * np.random.uniform(0.8, 1.2), 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * np.random.uniform(0.8, 1.2), 0, 255)
            img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        # 随机水平翻转
        if np.random.rand() > 0.5:
            img = cv2.flip(img, 1)
            labels = [(cls, 1 - cx, cy, w, h) for cls, cx, cy, w, h in labels]

        return img, labels


def collate_fn(batch):
    """
    自定义 collate 函数

    将多张图的 targets 合并，并添加 batch_idx
    """
    imgs, targets = zip(*batch)
    imgs = torch.stack(imgs, 0)

    # 给每个 target 添加 batch index
    for i, t in enumerate(targets):
        t[:, 0] = i

    targets = torch.cat(targets, 0)
    return imgs, targets


if __name__ == '__main__':
    print("Testing COCODetectionDataset (YOLOv5)...")

    dataset = COCODetectionDataset(
        yaml_path='../../data/coco.yaml',
        split='train',
        img_size=640,
        augment=True
    )

    if len(dataset) > 0:
        img, target = dataset[0]
        print(f"Sample:")
        print(f"  Image shape: {img.shape}")
        print(f"  Target shape: {target.shape}")
        print(f"  Target format: [batch_idx, class_id, cx, cy, w, h]")

    print("\nTest passed!")
