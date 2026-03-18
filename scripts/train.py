"""
YOLOv5 Training Script - 完整版
包含训练、验证、评估指标计算和可视化
"""

import os
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from tqdm import tqdm
import numpy as np
import yaml

from yolov5.models import create_yolov5
from yolov5.data import COCODetectionDataset, collate_fn
from yolov5.utils import (
    create_yolov5_loss,
    init_seeds,
    check_img_size,
    colorstr,
    increment_path,
    nms,
    ReduceLROnPlateau,
    EarlyStopping,
    ModelEMA,
    GradientAccumulator,
)
from yolov5.utils.metrics import DetectionMetrics
from yolov5.utils.plots import (
    TrainingPlotter,
    plot_detection_samples,
    plot_labels_distribution
)


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def merge_config(args, config: dict):
    """
    Merge YAML config values into argparse args.

    YAML sections (model, training, data) are flattened.
    Top-level keys (save_dir, name, device, seed) are also merged.
    Command-line explicit arguments take precedence over config file.
    """
    # Mapping from YAML key -> argparse attr (for keys with different names)
    key_map = {
        'data': 'data',             # data.data -> args.data
        'save_dir': 'project',      # save_dir -> args.project
    }

    # Flatten sections
    flat = {}
    for section in ['model', 'training', 'data']:
        if section in config:
            for key, value in config[section].items():
                flat[key] = value

    # Top-level keys
    for key in ['save_dir', 'name', 'device', 'seed']:
        if key in config:
            flat[key] = config[key]

    # Apply to args
    for key, value in flat.items():
        # Map YAML key to argparse attr name
        attr = key_map.get(key, key)
        # Convert hyphens to underscores (argparse convention)
        attr = attr.replace('-', '_')

        if hasattr(args, attr):
            setattr(args, attr, value)

    return args


def parse_args():
    parser = argparse.ArgumentParser(description='YOLOv5 Training')

    # Config file
    parser.add_argument('--config', type=str, default='',
                        help='Training config YAML (e.g. training.yaml)')

    # Data
    parser.add_argument('--data', type=str, default='data-format/coco128.yaml', help='Dataset config YAML')
    parser.add_argument('--img-size', type=int, default=640, help='Input image size')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--workers', type=int, default=8, help='Dataloader workers')
    parser.add_argument('--cache', action='store_true', help='Cache images')

    # Model
    parser.add_argument('--variant', type=str, default='s',
                        choices=['n', 's', 'm', 'l', 'x'], help='Model variant')

    # Training
    parser.add_argument('--epochs', type=int, default=100, help='Training epochs')
    parser.add_argument('--lr', type=float, default=1e-2, help='Initial learning rate')
    parser.add_argument('--weight-decay', type=float, default=5e-4, help='Weight decay')
    parser.add_argument('--warmup-epochs', type=int, default=3, help='Warmup epochs')
    parser.add_argument('--grad-clip', type=float, default=10.0, help='Gradient clipping')

    # Loss weights
    parser.add_argument('--lambda-box', type=float, default=0.05, help='Box loss weight')
    parser.add_argument('--lambda-obj', type=float, default=1.0, help='Objectness loss weight')
    parser.add_argument('--lambda-cls', type=float, default=0.5, help='Classification loss weight')

    # LR scheduling & early stopping
    parser.add_argument('--patience', type=int, default=5, help='LR plateau patience')
    parser.add_argument('--lr-factor', type=float, default=0.1, help='LR reduction factor')
    parser.add_argument('--min-lr', type=float, default=1e-7, help='Minimum learning rate')
    parser.add_argument('--max-lr-reductions', type=int, default=3, help='Max LR reductions')
    parser.add_argument('--early-stopping', action='store_true', help='Enable early stopping')
    parser.add_argument('--accumulation-steps', type=int, default=1, help='Gradient accumulation')
    parser.add_argument('--amp', action='store_true', help='Mixed precision training')
    parser.add_argument('--label-smoothing', type=float, default=0.0, help='Label smoothing')
    parser.add_argument('--ema', action='store_true', help='Model EMA')
    parser.add_argument('--ema-decay', type=float, default=0.9999, help='EMA decay')

    # Evaluation
    parser.add_argument('--eval-interval', type=int, default=5, help='Eval every N epochs')
    parser.add_argument('--conf-thres', type=float, default=0.001, help='Eval confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.6, help='NMS IoU threshold')
    parser.add_argument('--plot-samples', type=int, default=16, help='Vis samples count')

    # Output
    parser.add_argument('--project', type=str, default='runs/train', help='Save directory')
    parser.add_argument('--name', type=str, default='exp', help='Experiment name')
    parser.add_argument('--resume', type=str, default='', help='Resume from exp name')
    parser.add_argument('--device', type=str, default='0', help='CUDA device or cpu')
    parser.add_argument('--seed', type=int, default=0, help='Random seed')
    parser.add_argument('--exist-ok', action='store_true', help='Allow existing dir')

    args = parser.parse_args()

    # Load and merge config file if provided
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            # Try relative to project root
            config_path = ROOT / args.config
        if config_path.exists():
            print(f'Loading config from {config_path}')
            config = load_config(str(config_path))
            args = merge_config(args, config)
        else:
            print(f'WARNING: Config file not found: {args.config}')

    return args


def setup_device(device_str: str):
    if device_str == 'cpu':
        return torch.device('cpu')
    if torch.cuda.is_available():
        os.environ['CUDA_VISIBLE_DEVICES'] = device_str
        return torch.device('cuda:0')
    print(colorstr('yellow', 'WARNING: CUDA not available, using CPU'))
    return torch.device('cpu')


def train_one_epoch(model, dataloader, criterion, optimizer, device, epoch,
                    grad_clip=0.0, scaler=None, accumulator=None, ema=None):
    """训练一个 epoch"""
    model.train()
    pbar = tqdm(dataloader, desc=f'Epoch {epoch}')
    total_loss = 0
    loss_components = {}
    use_amp = scaler is not None

    for batch_idx, (images, targets) in enumerate(pbar):
        images = images.to(device)
        targets = targets.to(device)

        with torch.amp.autocast('cuda', enabled=use_amp):
            predictions = model(images)
            loss, loss_dict = criterion(predictions, targets)

        if accumulator is not None:
            if use_amp:
                scaler.scale(loss / accumulator.accumulation_steps).backward()
            else:
                (loss / accumulator.accumulation_steps).backward()

            if accumulator.should_step(batch_idx):
                if use_amp:
                    if grad_clip > 0:
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    if grad_clip > 0:
                        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                    optimizer.step()
                optimizer.zero_grad()
                if ema is not None:
                    ema.update(model)
        else:
            optimizer.zero_grad()
            if use_amp:
                scaler.scale(loss).backward()
                if grad_clip > 0:
                    scaler.unscale_(optimizer)
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                if grad_clip > 0:
                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                optimizer.step()
            if ema is not None:
                ema.update(model)

        total_loss += loss.item()
        for k, v in loss_dict.items():
            loss_components[k] = loss_components.get(k, 0) + v

        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'box': f'{loss_dict["box"]:.4f}',
            'obj': f'{loss_dict["obj"]:.4f}',
            'cls': f'{loss_dict["cls"]:.4f}'
        })

    num_batches = len(dataloader)
    return total_loss / num_batches, {k: v / num_batches for k, v in loss_components.items()}


@torch.no_grad()
def validate(model, dataloader, criterion, device,
             conf_thres=0.001, iou_thres=0.6, nc=80,
             compute_metrics=True, save_dir=None, plot_samples=16):
    """验证并计算评估指标"""
    model.eval()
    total_loss = 0
    loss_components = {}

    all_predictions = []
    all_targets = []
    sample_images = []
    sample_preds = []
    sample_targets = []

    detection_metrics = DetectionMetrics(nc=nc)
    pbar = tqdm(dataloader, desc='Validation')

    for batch_idx, (images, targets) in enumerate(pbar):
        images = images.to(device)
        targets_device = targets.to(device)

        predictions_raw = model(images)
        loss, loss_dict = criterion(predictions_raw, targets_device)

        total_loss += loss.item()
        for k, v in loss_dict.items():
            loss_components[k] = loss_components.get(k, 0) + v

        if compute_metrics:
            batch_predictions = model.predict(images, conf_threshold=conf_thres, device=device)

            # 转换 targets: (N, 6) -> per-image [class_id, x1, y1, x2, y2]
            batch_targets = []
            img_size = model.img_size
            B = images.size(0)

            for i in range(B):
                mask = targets[:, 0] == i
                t = targets[mask]  # (ni, 6)
                if len(t) == 0:
                    batch_targets.append(np.zeros((0, 5)))
                    continue

                # cx, cy, w, h -> x1, y1, x2, y2 (像素坐标)
                cls = t[:, 1].cpu().numpy()
                cx = t[:, 2].cpu().numpy() * img_size
                cy = t[:, 3].cpu().numpy() * img_size
                w = t[:, 4].cpu().numpy() * img_size
                h = t[:, 5].cpu().numpy() * img_size

                x1 = np.clip(cx - w / 2, 0, img_size)
                y1 = np.clip(cy - h / 2, 0, img_size)
                x2 = np.clip(cx + w / 2, 0, img_size)
                y2 = np.clip(cy + h / 2, 0, img_size)

                batch_targets.append(np.stack([cls, x1, y1, x2, y2], axis=1))

            # NMS
            for i in range(len(batch_predictions)):
                batch_predictions[i] = nms(batch_predictions[i], iou_threshold=iou_thres)

            detection_metrics.update(batch_predictions, batch_targets)

            if batch_idx == 0 and save_dir:
                n_samples = min(plot_samples, B)
                for i in range(n_samples):
                    sample_images.append(images[i].cpu().numpy())
                    sample_preds.append(batch_predictions[i])
                    sample_targets.append(batch_targets[i])

    num_batches = len(dataloader)
    avg_loss = total_loss / num_batches
    avg_components = {k: v / num_batches for k, v in loss_components.items()}

    metrics = {'val_loss': avg_loss}
    metrics.update(avg_components)

    if compute_metrics:
        det_metrics = detection_metrics.compute_metrics()
        metrics.update(det_metrics)

    if save_dir and sample_images:
        plot_detection_samples(
            sample_images, sample_preds, sample_targets,
            dataloader.dataset.class_names, save_dir, max_images=plot_samples
        )

    return metrics, sample_images, sample_preds, sample_targets


def main():
    args = parse_args()
    init_seeds(args.seed)

    # 保存目录
    save_dir = Path(increment_path(Path(args.project) / args.name, exist_ok=args.exist_ok))
    save_dir.mkdir(parents=True, exist_ok=True)
    weights_dir = save_dir / 'weights'
    weights_dir.mkdir(exist_ok=True)

    # 打印配置
    print(colorstr('bright_blue', 'bold', '\n' + '=' * 60))
    print(colorstr('bright_blue', 'bold', f'YOLOv5{args.variant} Training'))
    print('=' * 60)
    print(f'Device: {args.device}')
    print(f'Dataset: {args.data}')
    print(f'Model: YOLOv5{args.variant}')
    print(f'Image size: {args.img_size}')
    print(f'Batch size: {args.batch_size}')
    if args.accumulation_steps > 1:
        print(f'Effective batch size: {args.batch_size * args.accumulation_steps}')
    print(f'Epochs: {args.epochs}')
    print(f'Save directory: {save_dir}')
    print(colorstr('bright_yellow', '--- Features ---'))
    print(f'AMP: {"enabled" if args.amp else "disabled"}')
    print(f'EMA: {"enabled" if args.ema else "disabled"}')
    print(f'Label smoothing: {args.label_smoothing}')
    print(f'Early stopping: {"enabled" if args.early_stopping else "disabled"}')
    print('=' * 60)

    device = setup_device(args.device)
    img_size = check_img_size(args.img_size, stride=32)

    # 数据集
    print(colorstr('bright_green', '\nLoading datasets...'))
    train_dataset = COCODetectionDataset(
        yaml_path=args.data, split='train',
        img_size=img_size, augment=True, cache_images=args.cache
    )
    val_dataset = COCODetectionDataset(
        yaml_path=args.data, split='val',
        img_size=img_size, augment=False, cache_images=False
    )

    # 标签分布
    raw_labels = []
    for i in range(min(1000, len(train_dataset))):
        labels = train_dataset._load_labels(i)
        if labels:
            raw_labels.append(np.array(labels, dtype=np.float32))
        else:
            raw_labels.append(np.array([], dtype=np.float32).reshape(0, 5))
    plot_labels_distribution(raw_labels, train_dataset.class_names, save_dir)

    # Dataloader
    train_loader = DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True,
        num_workers=args.workers, pin_memory=True, drop_last=True,
        collate_fn=collate_fn
    )
    val_loader = DataLoader(
        val_dataset, batch_size=args.batch_size, shuffle=False,
        num_workers=args.workers, pin_memory=True,
        collate_fn=collate_fn
    )

    # 模型
    print(colorstr('bright_green', '\nCreating model...'))
    model = create_yolov5(
        num_classes=train_dataset.num_classes,
        img_size=img_size,
        variant=args.variant
    )
    model = model.to(device)

    total_params = sum(p.numel() for p in model.parameters())
    print(f'Parameters: {total_params:,} ({total_params * 4 / 1e6:.2f} MB)')

    # 损失函数
    criterion = create_yolov5_loss(
        num_classes=train_dataset.num_classes,
        lambda_box=args.lambda_box,
        lambda_obj=args.lambda_obj,
        lambda_cls=args.lambda_cls,
        label_smoothing=args.label_smoothing
    ).to(device)

    # 优化器 - SGD (YOLOv5 默认)
    optimizer = optim.SGD(
        model.parameters(),
        lr=args.lr,
        momentum=0.937,
        weight_decay=args.weight_decay,
        nesterov=True
    )

    # 学习率调度
    def lr_lambda(epoch):
        if epoch < args.warmup_epochs:
            return (epoch + 1) / args.warmup_epochs
        progress = (epoch - args.warmup_epochs) / (args.epochs - args.warmup_epochs)
        return max(0.01, 0.5 * (1 + np.cos(np.pi * progress)))

    warmup_scheduler = optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    lr_plateau = ReduceLROnPlateau(
        optimizer, mode='min', factor=args.lr_factor,
        patience=args.patience, min_lr=args.min_lr, verbose=True
    )

    early_stopping = EarlyStopping(
        patience=args.patience, mode='min',
        check_lr_reductions=True, max_lr_reductions=args.max_lr_reductions,
        verbose=True
    ) if args.early_stopping else None

    scaler = torch.amp.GradScaler('cuda') if args.amp and device.type == 'cuda' else None
    accumulator = GradientAccumulator(args.accumulation_steps) if args.accumulation_steps > 1 else None
    ema = ModelEMA(model, decay=args.ema_decay) if args.ema else None

    plotter = TrainingPlotter(save_dir)

    # 恢复训练
    start_epoch = 0
    best_map = 0.0
    best_val_loss = float('inf')
    ema_val_loss = None
    ema_alpha = 0.1

    resume_path = None
    if args.resume:
        candidate = Path(args.project) / args.resume / 'weights' / 'last.pt'
        if candidate.exists():
            resume_path = str(candidate)
        else:
            print(colorstr('red', f'WARNING: Cannot find checkpoint for "{args.resume}"'))

    if resume_path:
        print(colorstr('bright_cyan', f'\nResuming from {resume_path}'))
        ckpt = torch.load(resume_path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt['model'])
        optimizer.load_state_dict(ckpt['optimizer'])
        start_epoch = ckpt['epoch']
        best_map = ckpt.get('best_map', 0.0)
        best_val_loss = ckpt.get('best_val_loss', float('inf'))
        if 'lr_plateau' in ckpt:
            lr_plateau.load_state_dict(ckpt['lr_plateau'])
        if early_stopping and 'early_stopping' in ckpt:
            early_stopping.load_state_dict(ckpt['early_stopping'])
        if ema and 'ema' in ckpt:
            ema.load_state_dict(ckpt['ema'])
        if scaler and 'scaler' in ckpt:
            scaler.load_state_dict(ckpt['scaler'])
        print(f'Resumed from epoch {start_epoch}')

    # 训练循环
    print(colorstr('bright_green', 'bold', '\nStarting training...'))
    print('=' * 60)

    for epoch in range(start_epoch, args.epochs):
        current_lr = optimizer.param_groups[0]['lr']
        epoch_color = 'bright_yellow' if epoch < args.warmup_epochs else 'bright_cyan'
        print(f'\n{colorstr(epoch_color, "bold", f"Epoch {epoch}/{args.epochs-1}")} | LR: {current_lr:.2e}')

        train_loss, train_dict = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch,
            grad_clip=args.grad_clip, scaler=scaler,
            accumulator=accumulator, ema=ema
        )

        is_last_epoch = (epoch == args.epochs - 1)
        is_eval_epoch = (args.eval_interval > 0 and epoch % args.eval_interval == 0)
        compute_full_metrics = is_last_epoch or is_eval_epoch

        val_model = ema.ema if ema else model
        val_metrics, _, _, _ = validate(
            val_model, val_loader, criterion, device,
            conf_thres=args.conf_thres, iou_thres=args.iou_thres,
            nc=train_dataset.num_classes,
            compute_metrics=compute_full_metrics,
            save_dir=save_dir if compute_full_metrics else None,
            plot_samples=args.plot_samples
        )

        # 学习率调度
        if epoch < args.warmup_epochs:
            warmup_scheduler.step()
        else:
            current_val_loss = val_metrics.get("val_loss", 0)
            lr_reduced = lr_plateau.step(current_val_loss)

            if early_stopping:
                should_stop = early_stopping.step(
                    current_val_loss, lr_reduced=lr_reduced,
                    num_lr_reductions=lr_plateau.num_lr_reductions
                )
                if should_stop:
                    print(colorstr('red', 'bold', '\nEarly stopping triggered!'))
                    val_metrics, _, _, _ = validate(
                        val_model, val_loader, criterion, device,
                        conf_thres=args.conf_thres, iou_thres=args.iou_thres,
                        nc=train_dataset.num_classes, compute_metrics=True,
                        save_dir=save_dir, plot_samples=args.plot_samples
                    )
                    all_metrics = {'train_loss': train_loss, **val_metrics}
                    plotter.update(epoch, all_metrics)
                    plotter.save_metrics_csv()
                    print(f'\nFinal: P={val_metrics.get("precision", 0):.4f} '
                          f'R={val_metrics.get("recall", 0):.4f} '
                          f'mAP@0.5={val_metrics.get("mAP@0.5", 0):.4f}')
                    break

        all_metrics = {'train_loss': train_loss, **val_metrics}
        plotter.update(epoch, all_metrics)
        plotter.save_metrics_csv()

        current_val_loss = val_metrics.get("val_loss", 0)
        if ema_val_loss is None:
            ema_val_loss = current_val_loss
        else:
            ema_val_loss = ema_alpha * current_val_loss + (1 - ema_alpha) * ema_val_loss

        print(f"Train Loss: {train_loss:.4f} | Val Loss: {current_val_loss:.4f} (EMA: {ema_val_loss:.4f})")
        if 'precision' in val_metrics:
            print(f"mAP@0.5: {val_metrics.get('mAP@0.5', 0):.4f} | "
                  f"P: {val_metrics['precision']:.4f} | R: {val_metrics['recall']:.4f}")

        # 保存
        ckpt = {
            'epoch': epoch + 1,
            'model': model.state_dict(),
            'optimizer': optimizer.state_dict(),
            'metrics': all_metrics,
            'best_map': best_map,
            'ema_val_loss': ema_val_loss,
            'best_val_loss': best_val_loss,
            'lr_plateau': lr_plateau.state_dict(),
            'variant': args.variant,
            'num_classes': train_dataset.num_classes,
        }
        if early_stopping:
            ckpt['early_stopping'] = early_stopping.state_dict()
        if ema:
            ckpt['ema'] = ema.state_dict()
        if scaler:
            ckpt['scaler'] = scaler.state_dict()

        torch.save(ckpt, weights_dir / 'last.pt')

        current_map = val_metrics.get('mAP@0.5', 0)
        save_best = False
        save_reason = ""

        if current_map > 0 and current_map > best_map:
            save_best = True
            save_reason = f"mAP: {best_map:.4f} -> {current_map:.4f}"
            best_map = current_map
            ckpt['best_map'] = best_map
        if ema_val_loss < best_val_loss:
            if not save_best:
                save_best = True
                save_reason = f"val_loss(EMA): {best_val_loss:.4f} -> {ema_val_loss:.4f}"
            best_val_loss = ema_val_loss
            ckpt['best_val_loss'] = best_val_loss

        if save_best:
            torch.save(ckpt, weights_dir / 'best.pt')
            print(colorstr('bright_green', f"New best: {save_reason}"))
            if early_stopping:
                early_stopping.reset()

    # 完成
    print(f"\nTraining complete. Results saved to {save_dir}")
    print(f"Best val_loss(EMA): {best_val_loss:.4f}, Best mAP@0.5: {best_map:.4f}")

    plotter.plot_training_curves()
    plotter.save_metrics_csv()

    # 最终评估
    print(colorstr('bright_cyan', '\nFinal evaluation...'))
    best_weights = weights_dir / 'best.pt'
    last_weights = weights_dir / 'last.pt'

    if best_weights.exists():
        ckpt = torch.load(best_weights, weights_only=False)
        model.load_state_dict(ckpt['model'])
        if ema and 'ema' in ckpt:
            ema.load_state_dict(ckpt['ema'])
    elif last_weights.exists():
        ckpt = torch.load(last_weights, weights_only=False)
        model.load_state_dict(ckpt['model'])
        if ema and 'ema' in ckpt:
            ema.load_state_dict(ckpt['ema'])

    final_model = ema.ema if ema else model
    validate(
        final_model, val_loader, criterion, device,
        conf_thres=args.conf_thres, iou_thres=args.iou_thres,
        nc=train_dataset.num_classes, compute_metrics=True,
        save_dir=save_dir, plot_samples=args.plot_samples
    )

    print(colorstr('bright_green', '\nAll done!'))
    print(f'Results: {save_dir}')


if __name__ == '__main__':
    main()
