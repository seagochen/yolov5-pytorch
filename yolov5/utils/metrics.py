"""
Evaluation metrics for object detection
计算 mAP、Precision、Recall 等评估指标
"""

import numpy as np
import torch
from typing import List, Dict, Tuple
from collections import defaultdict


def box_iou_batch(box1: np.ndarray, box2: np.ndarray) -> np.ndarray:
    """
    计算批量框的 IoU

    Args:
        box1: (N, 4) [x1, y1, x2, y2]
        box2: (M, 4) [x1, y1, x2, y2]

    Returns:
        iou: (N, M) IoU 矩阵
    """
    area1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])
    area2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])

    x1 = np.maximum(box1[:, 0][:, None], box2[:, 0][None, :])
    y1 = np.maximum(box1[:, 1][:, None], box2[:, 1][None, :])
    x2 = np.minimum(box1[:, 2][:, None], box2[:, 2][None, :])
    y2 = np.minimum(box1[:, 3][:, None], box2[:, 3][None, :])

    inter_area = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    union_area = area1[:, None] + area2[None, :] - inter_area

    return inter_area / (union_area + 1e-16)


def ap_per_class(
    tp: np.ndarray,
    conf: np.ndarray,
    pred_cls: np.ndarray,
    target_cls: np.ndarray,
    eps: float = 1e-16
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """计算每个类别的 AP"""
    i = np.argsort(-conf)
    tp, conf, pred_cls = tp[i], conf[i], pred_cls[i]

    unique_classes = np.unique(target_cls)
    nc = unique_classes.shape[0]

    px, py = np.linspace(0, 1, 1000), []
    ap = np.zeros((nc, tp.shape[1]))
    p = np.zeros(nc)
    r = np.zeros(nc)

    for ci, c in enumerate(unique_classes):
        i = pred_cls == c
        n_l = (target_cls == c).sum()
        n_p = i.sum()

        if n_p == 0 or n_l == 0:
            continue

        fpc = (1 - tp[i]).cumsum(0)
        tpc = tp[i].cumsum(0)

        recall = tpc / (n_l + eps)
        r[ci] = recall[-1, 0] if len(recall) > 0 else 0

        precision = tpc / (tpc + fpc)
        p[ci] = precision[-1, 0] if len(precision) > 0 else 0

        for j in range(tp.shape[1]):
            ap[ci, j], _, _ = compute_ap(recall[:, j], precision[:, j])

    f1 = 2 * p * r / (p + r + eps)
    return p, r, ap, f1


def compute_ap(recall: np.ndarray, precision: np.ndarray) -> Tuple[float, np.ndarray, np.ndarray]:
    """计算 AP (101点插值)"""
    mrec = np.concatenate(([0.], recall, [1.]))
    mpre = np.concatenate(([1.], precision, [0.]))
    mpre = np.flip(np.maximum.accumulate(np.flip(mpre)))
    x = np.linspace(0, 1, 101)
    ap = np.trapz(np.interp(x, mrec, mpre), x)
    return ap, mpre, mrec


class ConfusionMatrix:
    """混淆矩阵"""

    def __init__(self, nc: int, conf: float = 0.25, iou_thres: float = 0.45):
        self.matrix = np.zeros((nc + 1, nc + 1))
        self.nc = nc
        self.conf = conf
        self.iou_thres = iou_thres

    def process_batch(self, detections: np.ndarray, labels: np.ndarray):
        if detections is None:
            gt_classes = labels[:, 0].astype(int)
            for gc in gt_classes:
                self.matrix[self.nc, gc] += 1
            return

        detections = detections[detections[:, 4] > self.conf]
        gt_classes = labels[:, 0].astype(int)
        detection_classes = detections[:, 5].astype(int)

        if len(detections) == 0:
            for gc in gt_classes:
                self.matrix[self.nc, gc] += 1
            return

        if len(labels) == 0:
            for dc in detection_classes:
                self.matrix[dc, self.nc] += 1
            return

        iou = box_iou_batch(labels[:, 1:], detections[:, :4])

        matches = []
        for i, gc in enumerate(gt_classes):
            j = iou[i].argmax()
            if iou[i, j] > self.iou_thres:
                matches.append([i, j, iou[i, j], gc, detection_classes[j]])

        matches = np.array(matches)

        if len(matches):
            if len(matches) > 1:
                matches = matches[matches[:, 2].argsort()[::-1]]
                matches = matches[np.unique(matches[:, 1], return_index=True)[1]]
                matches = matches[np.unique(matches[:, 0], return_index=True)[1]]

            for m in matches:
                self.matrix[int(m[4]), int(m[3])] += 1

            for i, dc in enumerate(detection_classes):
                if not any(matches[:, 1] == i):
                    self.matrix[dc, self.nc] += 1

            for i, gc in enumerate(gt_classes):
                if not any(matches[:, 0] == i):
                    self.matrix[self.nc, gc] += 1
        else:
            for dc in detection_classes:
                self.matrix[dc, self.nc] += 1
            for gc in gt_classes:
                self.matrix[self.nc, gc] += 1

    def matrix_to_metrics(self) -> Dict[str, float]:
        tp = np.diag(self.matrix)[:-1]
        fp = self.matrix[:-1, self.nc]
        fn = self.matrix[self.nc, :-1]
        precision = tp / (tp + fp + 1e-16)
        recall = tp / (tp + fn + 1e-16)
        f1 = 2 * precision * recall / (precision + recall + 1e-16)
        return {
            'precision': precision.mean(),
            'recall': recall.mean(),
            'f1': f1.mean(),
            'tp': tp.sum(), 'fp': fp.sum(), 'fn': fn.sum()
        }

    def reset(self):
        self.matrix = np.zeros((self.nc + 1, self.nc + 1))


class DetectionMetrics:
    """检测指标计算器"""

    def __init__(self, nc: int = 80):
        self.nc = nc
        self.stats = []

    def update(self, predictions: List[Dict], targets: List[np.ndarray], iou_thresholds: np.ndarray = None):
        if iou_thresholds is None:
            iou_thresholds = np.array([0.5])

        for pred, target in zip(predictions, targets):
            if len(pred) == 0:
                if len(target) > 0:
                    self.stats.append((
                        np.zeros((0, len(iou_thresholds)), dtype=bool),
                        np.array([]), np.array([]), target[:, 0]
                    ))
                continue

            def to_numpy_safe(value):
                if isinstance(value, torch.Tensor):
                    return value.cpu().item() if value.numel() == 1 else value.cpu().numpy()
                elif isinstance(value, (tuple, list)):
                    return tuple(to_numpy_safe(v) for v in value) if isinstance(value, tuple) else [to_numpy_safe(v) for v in value]
                return value

            pred_boxes = np.array([to_numpy_safe(p['bbox']) for p in pred])
            pred_conf = np.array([to_numpy_safe(p['confidence']) for p in pred])
            pred_cls = np.array([to_numpy_safe(p['class_id']) for p in pred])

            if len(target) == 0:
                self.stats.append((
                    np.zeros((len(pred), len(iou_thresholds)), dtype=bool),
                    pred_conf, pred_cls, np.array([])
                ))
                continue

            target_cls = target[:, 0]
            target_boxes = target[:, 1:]

            iou = box_iou_batch(target_boxes, pred_boxes)

            correct = np.zeros((len(pred), len(iou_thresholds)), dtype=bool)
            sort_idx = np.argsort(-pred_conf)

            for i, iou_thr in enumerate(iou_thresholds):
                detected_gt = set()
                for pred_idx in sort_idx:
                    p_cls = pred_cls[pred_idx]
                    best_iou = 0
                    best_gt_idx = -1
                    for gt_idx, gt_cls in enumerate(target_cls):
                        if gt_idx in detected_gt or p_cls != gt_cls:
                            continue
                        current_iou = iou[gt_idx, pred_idx]
                        if current_iou > iou_thr and current_iou > best_iou:
                            best_iou = current_iou
                            best_gt_idx = gt_idx
                    if best_gt_idx >= 0:
                        correct[pred_idx, i] = True
                        detected_gt.add(best_gt_idx)

            self.stats.append((correct, pred_conf, pred_cls, target_cls))

    def compute_metrics(self) -> Dict[str, float]:
        if not self.stats:
            return {}
        stats = [np.concatenate(x, 0) for x in zip(*self.stats)]
        tp, conf, pred_cls, target_cls = stats
        p, r, ap, f1 = ap_per_class(tp, conf, pred_cls, target_cls)
        ap50 = ap[:, 0] if ap.ndim > 1 else ap
        metrics = {
            'precision': p.mean(),
            'recall': r.mean(),
            'mAP@0.5': ap50.mean(),
            'f1': f1.mean()
        }
        for i in range(self.nc):
            if i < len(ap50):
                metrics[f'AP_class_{i}'] = ap50[i]
        return metrics

    def reset(self):
        self.stats = []
