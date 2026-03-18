# YOLOv5-PyTorch

A clean, modular implementation of YOLOv5 in PyTorch for object detection.

## Architecture

| Component | Description |
|-----------|-------------|
| Backbone  | CSPDarknet with C3 blocks, SiLU activation, SPPF |
| Neck      | PANet (FPN top-down + PAN bottom-up) |
| Head      | Triple-scale detection: P3/8, P4/16, P5/32 |
| Loss      | CIoU box loss + BCE objectness + BCE classification |

### Model Variants

| Model   | Width | Depth | Params     | Size (MB) |
|---------|-------|-------|------------|-----------|
| YOLOv5n | 0.25  | 0.33  | 1,913,117  | 7.7       |
| YOLOv5s | 0.50  | 0.33  | 7,399,229  | 29.6      |
| YOLOv5m | 0.75  | 0.67  | 21,559,197 | 86.2      |
| YOLOv5l | 1.00  | 1.00  | 47,219,069 | 188.9     |
| YOLOv5x | 1.25  | 1.33  | 87,773,405 | 351.1     |

## Project Structure

```
yolov5-pytorch/
├── yolov5/
│   ├── models/
│   │   ├── layers.py          # Conv, C3, SPPF, Bottleneck, Concat
│   │   ├── backbone.py        # CSPDarknet
│   │   ├── neck.py            # PANet (FPN + PAN)
│   │   └── yolov5.py          # YOLOv5 model + Detect head
│   ├── data/
│   │   └── datasets.py        # Ultralytics-compatible dataset loader
│   └── utils/
│       ├── loss.py            # CIoU + BCE loss
│       ├── general.py         # NMS, IoU, utilities
│       ├── metrics.py         # mAP, Precision, Recall
│       ├── callbacks.py       # EMA, LR scheduler, EarlyStopping
│       └── plots.py           # Training visualization
├── scripts/
│   ├── train.py               # Training script
│   └── detect.py              # Inference script
├── data-format/               # Dataset config examples
│   ├── coco128.yaml           # COCO 128-image subset
│   └── example_custom.yaml    # Custom dataset template
├── training.yaml              # Training hyperparameter config
├── requirements.txt
└── setup.py
```

## Quick Start

### Install

```bash
pip install -r requirements.txt
```

### Training

```bash
# Using YAML config file
python scripts/train.py --config training.yaml --data data-format/coco128.yaml

# Using command-line arguments
python scripts/train.py \
    --data path/to/data.yaml \
    --variant s \
    --epochs 100 \
    --batch-size 16 \
    --amp --ema

# Config file + CLI overrides (CLI takes precedence)
python scripts/train.py --config training.yaml --variant m --epochs 50
```

### Inference

```bash
python scripts/detect.py \
    --weights runs/train/exp/weights/best.pt \
    --source path/to/images/ \
    --conf-thres 0.5 \
    --save-img
```

## Dataset Format

Fully compatible with the **Ultralytics YOLO** data format. Datasets from [Roboflow](https://roboflow.com/), COCO, or any Ultralytics-compatible source work out of the box.

### Dataset YAML Config

Each dataset requires a YAML configuration file:

```yaml
path: /path/to/dataset        # dataset root (absolute or relative to YAML)
train: images/train            # training images dir or .txt file
val: images/val                # validation images dir or .txt file
test: images/test              # (optional) test images

nc: 3                          # number of classes
names:                         # class names (dict or list)
  0: cat
  1: dog
  2: bird
```

**Supported `names` formats:**
```yaml
# Dict format (recommended)
names:
  0: cat
  1: dog

# List format
names: ['cat', 'dog']
```

**Supported `train`/`val`/`test` values:**
```yaml
train: images/train            # directory path
train: train.txt               # text file with one image path per line
train: ../train/images         # Roboflow export format
```

### Directory Structure

**Option A - Parallel (recommended):**
```
my_dataset/
├── data.yaml
├── images/
│   ├── train/
│   │   ├── img001.jpg
│   │   └── ...
│   └── val/
│       └── ...
└── labels/                    # auto-resolved from /images/ -> /labels/
    ├── train/
    │   ├── img001.txt
    │   └── ...
    └── val/
        └── ...
```

**Option B - Nested:**
```
my_dataset/
├── data.yaml
├── train/
│   ├── images/
│   └── labels/
└── val/
    ├── images/
    └── labels/
```

### Label Format

One `.txt` file per image, same filename (e.g. `img001.jpg` -> `img001.txt`).

Each line represents one object:
```
class_id  center_x  center_y  width  height
```

- **class_id**: 0-indexed integer
- **center_x, center_y**: bounding box center, normalized to `[0, 1]`
- **width, height**: bounding box size, normalized to `[0, 1]`

**Example** (`img001.txt`):
```
0 0.481719 0.634028 0.690625 0.713278
1 0.741094 0.524306 0.314750 0.933389
```

Images without objects should have an **empty** `.txt` file (or no file at all).

### Using Roboflow Datasets

1. Export your dataset from [Roboflow](https://roboflow.com/) in **YOLOv5 PyTorch** format
2. The export includes a `data.yaml` — use it directly:
   ```bash
   python scripts/train.py --config training.yaml --data /path/to/roboflow/data.yaml
   ```

### Using COCO Format

Convert COCO JSON annotations to YOLO TXT format:
```python
# Using ultralytics converter
from ultralytics.data.converter import convert_coco
convert_coco(labels_dir="path/to/annotations/", save_dir="path/to/output/")
```

Or use tools like [JSON2YOLO](https://github.com/ultralytics/JSON2YOLO).

## Training Configuration

All hyperparameters can be set in `training.yaml`:

```yaml
model:
  variant: s               # n, s, m, l, x

training:
  epochs: 100
  batch_size: 16
  lr: 0.01
  amp: false               # mixed precision
  ema: false               # exponential moving average
  label_smoothing: 0.0

data:
  data: data-format/coco128.yaml
  workers: 8
```

See [training.yaml](training.yaml) for all available options.

## Training Output

```
runs/train/exp/
├── weights/
│   ├── best.pt                # best model (highest mAP)
│   └── last.pt                # latest checkpoint
├── training_curves.png        # loss, mAP, P/R curves
├── val_batch_predictions.jpg  # sample detection results
├── labels_distribution.png    # class distribution plot
└── metrics.csv                # per-epoch metrics
```

## Resume Training

```bash
python scripts/train.py --config training.yaml --resume exp
# Looks for runs/train/exp/weights/last.pt
```
