"""
Dataset classes - fully compatible with Ultralytics YOLO format.

Supports:
- Ultralytics YAML config (path, train, val, test, nc, names, download)
- names as list or dict: ['cat', 'dog'] or {0: 'cat', 1: 'dog'}
- train/val/test as directory path or .txt file listing image paths
- Roboflow export format (../ prefix)
- Automatic /images/ -> /labels/ path resolution
- Relative path resolution from YAML file or 'path' field
"""

import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Union
import yaml

# Supported image extensions (Ultralytics standard)
IMG_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif',
                  '.webp', '.dng', '.mpo', '.pfm'}


class COCODetectionDataset(Dataset):
    """
    Detection Dataset - fully compatible with Ultralytics YOLO format.

    Supported YAML formats:
    ```yaml
    # Standard Ultralytics format
    path: /path/to/dataset       # dataset root
    train: images/train           # dir or .txt file (relative to path)
    val: images/val
    test: images/test             # optional

    nc: 80
    names:                        # list or dict
      0: person
      1: bicycle
      ...

    # Optional
    download: https://...         # auto-download URL
    ```

    Label TXT format (one object per line, normalized coordinates):
    ```
    class_id center_x center_y width height
    ```
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
        self.yaml_path = Path(yaml_path).resolve()

        # Load config
        self.config = self._load_yaml(yaml_path)

        # Parse dataset root
        self.dataset_root = self._parse_dataset_root()

        # Parse class info
        self.num_classes = self.config['nc']
        self.class_names = self._parse_names(self.config['names'])

        # Resolve image and label paths
        self.img_files, self.label_dir = self._resolve_split(split)

        # Image cache
        self.imgs = [None] * len(self.img_files) if cache_images else None

        self._print_stats()

    def _load_yaml(self, yaml_path: str) -> Dict:
        """Load and validate YAML config."""
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML config not found: {yaml_path}")
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        for field in ['nc', 'names']:
            if field not in config:
                raise ValueError(f"Missing required field in YAML: {field}")
        return config

    def _parse_dataset_root(self) -> Path:
        """
        Resolve dataset root directory.

        Priority:
        1. Absolute 'path' field if it exists
        2. Relative 'path' field resolved from YAML file location
        3. YAML file's parent directory
        """
        if 'path' in self.config:
            root = Path(self.config['path'])
            if root.is_absolute():
                if root.exists():
                    return root
                print(f"Warning: Absolute path not found: {root}, "
                      f"falling back to YAML directory")
            else:
                # Resolve relative to YAML file location
                resolved = (self.yaml_path.parent / root).resolve()
                if resolved.exists():
                    return resolved
                print(f"Warning: Relative path not found: {resolved}, "
                      f"falling back to YAML directory")
        return self.yaml_path.parent

    @staticmethod
    def _parse_names(names: Union[List, Dict]) -> List[str]:
        """
        Parse class names - supports both list and dict format.

        Ultralytics supports:
          names: ['person', 'bicycle', 'car']          # list
          names: {0: 'person', 1: 'bicycle', 2: 'car'} # dict
        """
        if isinstance(names, dict):
            # Sort by key to ensure correct order
            return [names[k] for k in sorted(names.keys())]
        elif isinstance(names, list):
            return names
        else:
            raise ValueError(f"'names' must be a list or dict, got {type(names)}")

    def _resolve_split(self, split: str) -> Tuple[List[Path], Optional[Path]]:
        """
        Resolve image files and label directory for a given split.

        Supports:
        1. Directory path: 'images/train' -> scan for images
        2. Text file path: 'train.txt' -> read image paths line by line
        3. Roboflow format: '../train/images' -> strip ../ prefix
        """
        split_value = self.config.get(split)
        if split_value is None:
            # Fallback to default directory structure
            split_value = f'images/{split}'

        split_str = str(split_value)

        # Handle Roboflow ../ prefix
        if split_str.startswith('../'):
            split_str = split_str[3:]

        split_path = self.dataset_root / split_str

        # Case 1: It's a .txt file listing image paths
        if split_path.suffix == '.txt' and split_path.exists():
            return self._load_from_txt(split_path)

        # Also try without resolving (in case the path itself ends with .txt)
        raw_path = Path(split_str)
        if raw_path.suffix == '.txt':
            for candidate in [self.dataset_root / split_str,
                              self.yaml_path.parent / split_str]:
                if candidate.exists():
                    return self._load_from_txt(candidate)

        # Case 2: It's a directory
        img_dir = split_path
        if not img_dir.exists():
            # Try alternate location
            img_dir = self.yaml_path.parent / split_str
        if not img_dir.exists():
            print(f"Warning: Image path not found: {split_path}")
            return [], None

        img_files = self._scan_dir(img_dir)

        # Derive label directory: replace last 'images' with 'labels'
        label_dir = Path(self._images_to_labels(str(img_dir)))

        if not label_dir.exists():
            print(f"Warning: Label directory not found: {label_dir}")

        return img_files, label_dir

    def _load_from_txt(self, txt_path: Path) -> Tuple[List[Path], Optional[Path]]:
        """
        Load image paths from a text file.

        Each line contains one image path (absolute or relative to dataset_root).
        """
        img_files = []
        with open(txt_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                p = Path(line)
                if not p.is_absolute():
                    p = self.dataset_root / p
                if p.exists() and p.suffix.lower() in IMG_EXTENSIONS:
                    img_files.append(p)

        img_files = sorted(img_files)

        # Infer label directory from first image path
        label_dir = None
        if img_files:
            label_dir = Path(self._images_to_labels(str(img_files[0].parent)))

        return img_files, label_dir

    @staticmethod
    def _images_to_labels(img_path: str) -> str:
        """
        Convert image path to label path.

        Ultralytics convention: replace last occurrence of '/images/' with '/labels/'.
        Also handles '/images' at end of path.
        """
        # Replace /images/ with /labels/ (last occurrence)
        parts = img_path.rsplit('/images/', 1)
        if len(parts) == 2:
            return parts[0] + '/labels/' + parts[1]
        # Handle /images at end
        if img_path.endswith('/images'):
            return img_path[:-7] + '/labels'
        # Fallback: replace 'images' with 'labels'
        return img_path.replace('images', 'labels')

    @staticmethod
    def _scan_dir(img_dir: Path) -> List[Path]:
        """Scan directory for image files."""
        img_files = []
        for ext in IMG_EXTENSIONS:
            img_files.extend(img_dir.glob(f'*{ext}'))
            img_files.extend(img_dir.glob(f'*{ext.upper()}'))
        return sorted(set(img_files))  # deduplicate

    def _print_stats(self):
        label_info = str(self.label_dir) if self.label_dir else "N/A"
        print(f"\n{'='*60}")
        print(f"Dataset: {self.split}")
        print(f"{'='*60}")
        print(f"Root: {self.dataset_root}")
        print(f"Images: {len(self.img_files)} files")
        print(f"Labels: {label_info}")
        print(f"Classes: {self.num_classes} ({', '.join(self.class_names[:5])}{'...' if len(self.class_names) > 5 else ''})")
        print(f"Image size: {self.img_size}")
        print(f"Augmentation: {self.augment}")
        print(f"{'='*60}\n")

    def __len__(self) -> int:
        return len(self.img_files)

    def __getitem__(self, index: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Returns:
            image: (3, img_size, img_size) Tensor, normalized [0, 1]
            labels: (N, 6) Tensor [batch_idx(=0), class_id, cx, cy, w, h]
        """
        img = self._load_image(index)
        labels = self._load_labels(index)

        if self.augment:
            img, labels = self._apply_augmentations(img, labels)

        img = cv2.resize(img, (self.img_size, self.img_size))
        img = self._img_to_tensor(img)

        if len(labels) > 0:
            nl = len(labels)
            target = torch.zeros(nl, 6, dtype=torch.float32)
            labels_arr = np.array(labels, dtype=np.float32)
            target[:, 1] = torch.from_numpy(labels_arr[:, 0])     # class_id
            target[:, 2:6] = torch.from_numpy(labels_arr[:, 1:5]) # cx, cy, w, h
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
        """
        Load labels for an image.

        Ultralytics label format (per line):
            class_id center_x center_y width height

        Returns:
            List of (class_id, cx, cy, w, h) tuples
        """
        img_path = self.img_files[index]

        # Find label file: replace /images/ with /labels/ in path
        if self.label_dir is not None:
            label_path = self.label_dir / (img_path.stem + '.txt')
        else:
            # Direct path substitution (Ultralytics convention)
            label_path = Path(self._images_to_labels(str(img_path))).with_suffix('.txt')

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
                    # Only take first 5 values (ignore segmentation polygon points)
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
        """Basic data augmentations."""
        # HSV augmentation
        if np.random.rand() > 0.5:
            hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + np.random.uniform(-10, 10)) % 180
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * np.random.uniform(0.8, 1.2), 0, 255)
            hsv[:, :, 2] = np.clip(hsv[:, :, 2] * np.random.uniform(0.8, 1.2), 0, 255)
            img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

        # Random horizontal flip
        if np.random.rand() > 0.5:
            img = cv2.flip(img, 1)
            labels = [(cls, 1 - cx, cy, w, h) for cls, cx, cy, w, h in labels]

        return img, labels


def collate_fn(batch):
    """
    Custom collate function.

    Merges per-image targets and assigns batch indices.
    """
    imgs, targets = zip(*batch)
    imgs = torch.stack(imgs, 0)

    for i, t in enumerate(targets):
        t[:, 0] = i

    targets = torch.cat(targets, 0)
    return imgs, targets
