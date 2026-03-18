"""
YOLOv5 Loss Function
CIoU 坐标损失 + BCE 置信度损失 + BCE 分类损失
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Dict, List
import math


def bbox_ciou(box1: torch.Tensor, box2: torch.Tensor, eps: float = 1e-7) -> torch.Tensor:
    """
    计算 CIoU (Complete IoU)

    CIoU = IoU - (rho^2(b, b_gt) / c^2) - alpha * v
    其中 v 衡量宽高比一致性, alpha 是平衡系数

    Args:
        box1, box2: (N, 4) [x1, y1, x2, y2]

    Returns:
        ciou: (N,) CIoU 值
    """
    # 交集
    inter_x1 = torch.max(box1[:, 0], box2[:, 0])
    inter_y1 = torch.max(box1[:, 1], box2[:, 1])
    inter_x2 = torch.min(box1[:, 2], box2[:, 2])
    inter_y2 = torch.min(box1[:, 3], box2[:, 3])
    inter_area = (inter_x2 - inter_x1).clamp(0) * (inter_y2 - inter_y1).clamp(0)

    # 各自面积
    area1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])
    area2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])
    union = area1 + area2 - inter_area + eps

    iou = inter_area / union

    # 最小闭包矩形
    enclose_x1 = torch.min(box1[:, 0], box2[:, 0])
    enclose_y1 = torch.min(box1[:, 1], box2[:, 1])
    enclose_x2 = torch.max(box1[:, 2], box2[:, 2])
    enclose_y2 = torch.max(box1[:, 3], box2[:, 3])
    c2 = (enclose_x2 - enclose_x1) ** 2 + (enclose_y2 - enclose_y1) ** 2 + eps

    # 中心距离
    cx1 = (box1[:, 0] + box1[:, 2]) / 2
    cy1 = (box1[:, 1] + box1[:, 3]) / 2
    cx2 = (box2[:, 0] + box2[:, 2]) / 2
    cy2 = (box2[:, 1] + box2[:, 3]) / 2
    rho2 = (cx1 - cx2) ** 2 + (cy1 - cy2) ** 2

    # 宽高比
    w1, h1 = box1[:, 2] - box1[:, 0], box1[:, 3] - box1[:, 1]
    w2, h2 = box2[:, 2] - box2[:, 0], box2[:, 3] - box2[:, 1]
    v = (4 / math.pi ** 2) * (torch.atan(w2 / (h2 + eps)) - torch.atan(w1 / (h1 + eps))) ** 2

    with torch.no_grad():
        alpha = v / (1 - iou + v + eps)

    ciou = iou - rho2 / c2 - alpha * v
    return ciou


class YOLOv5Loss(nn.Module):
    """
    YOLOv5 损失函数

    改进相比 YOLOv2:
    - CIoU 替代 MSE 坐标损失 (更好的回归)
    - 多尺度检测损失 (P3/P4/P5)
    - 正样本匹配策略: 基于 anchor IoU + 邻近 grid cell
    - 自动损失平衡 (balance)
    - 标签平滑
    """

    def __init__(
        self,
        num_classes: int = 80,
        anchors: List[List[Tuple[int, int]]] = None,
        strides: List[int] = None,
        lambda_box: float = 0.05,
        lambda_obj: float = 1.0,
        lambda_cls: float = 0.5,
        label_smoothing: float = 0.0,
        anchor_threshold: float = 4.0
    ):
        super().__init__()

        self.num_classes = num_classes
        self.lambda_box = lambda_box
        self.lambda_obj = lambda_obj
        self.lambda_cls = lambda_cls
        self.anchor_threshold = anchor_threshold

        if strides is None:
            strides = [8, 16, 32]
        self.strides = strides

        if anchors is None:
            anchors = [
                [(10, 13), (16, 30), (33, 23)],
                [(30, 61), (62, 45), (59, 119)],
                [(116, 90), (156, 198), (373, 326)]
            ]

        # 注册 anchors
        a = torch.tensor(anchors, dtype=torch.float32)
        self.register_buffer('anchors', a)

        self.num_anchors = a.shape[1]
        self.num_layers = a.shape[0]

        # 各层损失平衡权重 (P3 权重更高, 因为小目标更难检测)
        self.balance = [4.0, 1.0, 0.4]

        # 标签平滑
        self.cp = 1.0 - 0.5 * label_smoothing  # positive label
        self.cn = 0.5 * label_smoothing          # negative label

        # BCE loss
        self.bce_obj = nn.BCEWithLogitsLoss(reduction='mean')
        self.bce_cls = nn.BCEWithLogitsLoss(reduction='mean')

    def forward(
        self,
        predictions: List[torch.Tensor],
        targets: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        计算损失

        Args:
            predictions: List of (B, na, H, W, 5+nc) per scale
            targets: (N, 6) [batch_idx, class_id, cx, cy, w, h] (归一化坐标)

        Returns:
            loss: 总损失
            loss_dict: 损失分解
        """
        device = predictions[0].device
        B = predictions[0].shape[0]

        loss_box = torch.zeros(1, device=device)
        loss_obj = torch.zeros(1, device=device)
        loss_cls = torch.zeros(1, device=device)

        # 构建每层的 targets
        for layer_idx, pred in enumerate(predictions):
            _, na, H, W, _ = pred.shape
            stride = self.strides[layer_idx]

            # 获取当前层的 anchor (转为 grid 单位)
            anchor = self.anchors[layer_idx] / stride  # (na, 2)

            # 构建 target
            tobj = torch.zeros_like(pred[..., 4])  # objectness target

            if targets.shape[0] == 0:
                loss_obj += self.bce_obj(pred[..., 4], tobj) * self.balance[layer_idx]
                continue

            # 匹配 targets 到 anchors
            t_indices, t_box, t_cls, t_anchors = self._build_targets(
                targets, anchor, H, W, stride, layer_idx, device
            )

            if len(t_indices[0]) == 0:
                loss_obj += self.bce_obj(pred[..., 4], tobj) * self.balance[layer_idx]
                continue

            b_idx, a_idx, gy, gx = t_indices

            # 提取匹配位置的预测
            pred_matched = pred[b_idx, a_idx, gy, gx]  # (M, 5+nc)

            # ====== 坐标损失 (CIoU) ======
            # 解码预测框 (grid 单位)
            pxy = torch.sigmoid(pred_matched[:, :2]) * 2 - 0.5
            pwh = (torch.sigmoid(pred_matched[:, 2:4]) * 2) ** 2 * t_anchors

            # 转为 xyxy (grid 单位)
            pred_box = torch.cat([pxy - pwh / 2, pxy + pwh / 2], dim=1)
            target_box = t_box

            ciou = bbox_ciou(pred_box, target_box)
            loss_box += (1.0 - ciou).mean()

            # objectness target 使用 CIoU 作为 soft label
            tobj[b_idx, a_idx, gy, gx] = ciou.detach().clamp(0).type(tobj.dtype)

            # ====== 分类损失 ======
            if self.num_classes > 1:
                # 多类别 BCE
                cls_targets = torch.full_like(pred_matched[:, 5:], self.cn)
                cls_targets[range(len(t_cls)), t_cls] = self.cp
                loss_cls += self.bce_cls(pred_matched[:, 5:], cls_targets)

            # ====== Objectness 损失 ======
            loss_obj += self.bce_obj(pred[..., 4], tobj) * self.balance[layer_idx]

        # 加权求和
        loss_box *= self.lambda_box
        loss_obj *= self.lambda_obj
        loss_cls *= self.lambda_cls

        total_loss = (loss_box + loss_obj + loss_cls) * B

        loss_dict = {
            'total': total_loss.item(),
            'box': loss_box.item(),
            'obj': loss_obj.item(),
            'cls': loss_cls.item(),
            'num_targets': targets.shape[0]
        }

        return total_loss, loss_dict

    def _build_targets(
        self,
        targets: torch.Tensor,
        anchors: torch.Tensor,
        H: int, W: int,
        stride: float,
        layer_idx: int,
        device: torch.device
    ):
        """
        构建匹配 targets

        YOLOv5 的正样本匹配策略:
        1. 根据 anchor 宽高比筛选 (ratio < anchor_threshold)
        2. 每个 target 可以匹配多个邻近 grid cell

        Returns:
            indices: (batch_idx, anchor_idx, grid_y, grid_x)
            tbox: target boxes in grid units (offset form)
            tcls: target class ids
            anchors_matched: matched anchor sizes
        """
        na = anchors.shape[0]
        nt = targets.shape[0]

        # target 格式: (N, 6) [batch_idx, class_id, cx, cy, w, h]
        # 转为 grid 坐标
        gain = torch.tensor([1, 1, W, H, W, H], device=device, dtype=torch.float32)
        t = targets * gain  # 归一化 -> grid 坐标

        # 扩展 targets 到每个 anchor: (na, nt, 6)
        t = t.unsqueeze(0).repeat(na, 1, 1)
        ai = torch.arange(na, device=device).float().view(na, 1, 1).repeat(1, nt, 1)
        t = torch.cat([t, ai], dim=2)  # (na, nt, 7) 加上 anchor index

        # ====== Anchor 宽高比筛选 ======
        # 只选择宽高比在阈值内的 anchor-target 对
        if nt:
            # target wh in grid units
            twh = t[:, :, 4:6]  # (na, nt, 2)
            # anchor wh
            awh = anchors.view(na, 1, 2).repeat(1, nt, 1)  # (na, nt, 2)

            # 宽高比
            r = twh / (awh + 1e-16)
            # 最大比值 < threshold
            j = torch.max(r, 1.0 / r).max(dim=2)[0] < self.anchor_threshold
            t = t[j]  # 过滤
        else:
            t = t.view(-1, 7)

        if t.shape[0] == 0:
            return (
                torch.zeros(0, dtype=torch.long, device=device),
                torch.zeros(0, dtype=torch.long, device=device),
                torch.zeros(0, dtype=torch.long, device=device),
                torch.zeros(0, dtype=torch.long, device=device),
            ), torch.zeros(0, 4, device=device), torch.zeros(0, dtype=torch.long, device=device), \
                torch.zeros(0, 2, device=device)

        # ====== 邻近 grid cell 扩展 ======
        # 每个 target 除了中心 cell，还加入相邻的 cell
        bc = t[:, :2]  # batch, class
        gxy = t[:, 2:4]  # grid xy
        gwh = t[:, 4:6]  # grid wh
        ai_t = t[:, 6]  # anchor indices

        # 偏移向量
        off = torch.tensor(
            [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1]],
            device=device, dtype=torch.float32
        )

        gxi = gxy.long()
        # 判断哪些方向可以扩展 (检查偏移后是否在 grid 范围内)
        g = 0.5
        gxy_frac = gxy % 1  # 小数部分

        # 4个方向: right(+x), down(+y), left(-x), up(-y)
        # right: 小数部分 > 0.5 且 x+1 < W
        j = (gxy_frac[:, 0] > g) & (gxi[:, 0] < W - 1)   # right
        k = (gxy_frac[:, 1] > g) & (gxi[:, 1] < H - 1)   # down
        l = (gxy_frac[:, 0] < g) & (gxi[:, 0] > 0)        # left
        m = (gxy_frac[:, 1] < g) & (gxi[:, 1] > 0)        # up

        # 选择有效的偏移
        selected = torch.stack([
            torch.ones_like(j),  # center always
            j, k, l, m          # 邻近 (right, down, left, up)
        ])

        # 扩展
        t_expanded = t.unsqueeze(0).repeat(5, 1, 1)[selected]
        offsets = (torch.zeros_like(gxy).unsqueeze(0) + off.unsqueeze(1))[selected]

        # 重新计算 grid 位置
        bc_e = t_expanded[:, :2]
        gxy_e = t_expanded[:, 2:4] - offsets
        gwh_e = t_expanded[:, 4:6]
        ai_e = t_expanded[:, 6]

        # 获取 grid 索引
        gx = gxy_e[:, 0].long().clamp(0, W - 1)
        gy = gxy_e[:, 1].long().clamp(0, H - 1)

        b_idx = bc_e[:, 0].long()
        a_idx = ai_e.long()
        t_cls = bc_e[:, 1].long()

        # target box (相对于 grid cell 的偏移)
        tbox = torch.cat([gxy_e - torch.stack([gx, gy], dim=1).float(), gwh_e], dim=1)
        # 转为 xyxy
        tbox_xyxy = torch.cat([
            tbox[:, :2] - tbox[:, 2:4] / 2,
            tbox[:, :2] + tbox[:, 2:4] / 2
        ], dim=1)

        # matched anchors
        anchors_matched = anchors[a_idx]

        return (b_idx, a_idx, gy, gx), tbox_xyxy, t_cls, anchors_matched


def create_yolov5_loss(
    num_classes: int = 80,
    anchors: List = None,
    strides: List[int] = None,
    **kwargs
) -> YOLOv5Loss:
    """创建 YOLOv5 损失函数"""
    return YOLOv5Loss(
        num_classes=num_classes,
        anchors=anchors,
        strides=strides,
        **kwargs
    )


if __name__ == '__main__':
    print("Testing YOLOv5Loss...")

    criterion = create_yolov5_loss(num_classes=80)

    # 模拟预测
    B = 2
    preds = [
        torch.randn(B, 3, 80, 80, 85),  # P3
        torch.randn(B, 3, 40, 40, 85),  # P4
        torch.randn(B, 3, 20, 20, 85),  # P5
    ]

    # 模拟 targets: (N, 6) [batch_idx, class_id, cx, cy, w, h]
    targets = torch.tensor([
        [0, 5, 0.5, 0.5, 0.1, 0.2],
        [0, 10, 0.3, 0.4, 0.05, 0.08],
        [1, 0, 0.7, 0.6, 0.3, 0.4],
    ])

    loss, loss_dict = criterion(preds, targets)
    print(f"\nLoss: {loss.item():.4f}")
    for k, v in loss_dict.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    # 测试反向传播
    for p in preds:
        p.requires_grad = True
    loss, _ = criterion(preds, targets)
    loss.backward()
    print(f"\nBackward pass OK, grad shapes: {[p.grad.shape for p in preds]}")

    print("\nAll tests passed!")
