"""
YOLOv5 Detection Model
多尺度目标检测网络，使用 CSPDarknet + PANet + 三尺度检测头
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple, Optional, Dict

from .backbone import CSPDarknet
from .neck import PANet
from .layers import Conv


class Detect(nn.Module):
    """
    YOLOv5 检测头

    在三个尺度上输出检测结果:
        P3 (stride=8):  适合小目标
        P4 (stride=16): 适合中目标
        P5 (stride=32): 适合大目标
    """
    def __init__(
        self,
        num_classes: int = 80,
        anchors: List[List[Tuple[int, int]]] = None,
        in_channels: Tuple[int, ...] = (128, 256, 512)
    ):
        super().__init__()

        self.num_classes = num_classes
        self.num_outputs = 5 + num_classes  # (tx, ty, tw, th, obj, cls...)
        self.num_layers = len(in_channels)  # 检测层数 (3)

        # 默认 anchors (像素单位, 对应 640x640 输入)
        if anchors is None:
            anchors = [
                [(10, 13), (16, 30), (33, 23)],       # P3/8  小目标
                [(30, 61), (62, 45), (59, 119)],       # P4/16 中目标
                [(116, 90), (156, 198), (373, 326)]    # P5/32 大目标
            ]

        self.num_anchors = len(anchors[0])  # 每个尺度的 anchor 数量 (3)

        # 注册 anchors 为 buffer
        # shape: (num_layers, num_anchors, 2)
        a = torch.tensor(anchors, dtype=torch.float32)
        self.register_buffer('anchors', a)

        # 每个尺度一个 1x1 检测头
        self.heads = nn.ModuleList(
            nn.Conv2d(c, self.num_anchors * self.num_outputs, 1)
            for c in in_channels
        )

        self._initialize_biases()

    def _initialize_biases(self):
        """初始化检测头偏置（加速收敛）"""
        for head in self.heads:
            b = head.bias.view(self.num_anchors, -1)
            # objectness 偏置: 使初始 sigmoid 输出约为 0.01
            b.data[:, 4] += -4.6  # -log((1-0.01)/0.01)
            # class 偏置
            b.data[:, 5:] += -4.6
            head.bias = nn.Parameter(b.view(-1), requires_grad=True)

    def forward(
        self,
        features: List[torch.Tensor]
    ) -> List[torch.Tensor]:
        """
        Args:
            features: [p3, p4, p5] 来自 neck

        Returns:
            outputs: List of (B, num_anchors, H, W, 5+nc) per scale
        """
        outputs = []
        for i, (feat, head) in enumerate(zip(features, self.heads)):
            B, _, H, W = feat.shape
            out = head(feat)  # (B, na*no, H, W)
            out = out.view(B, self.num_anchors, self.num_outputs, H, W)
            out = out.permute(0, 1, 3, 4, 2).contiguous()
            # (B, num_anchors, H, W, 5+nc)
            outputs.append(out)
        return outputs


class YOLOv5(nn.Module):
    """
    YOLOv5 目标检测网络

    架构: CSPDarknet (backbone) + PANet (neck) + Detect (head)
    """

    # 步长对应的三个检测层
    STRIDES = [8, 16, 32]

    def __init__(
        self,
        num_classes: int = 80,
        anchors: Optional[List[List[Tuple[int, int]]]] = None,
        img_size: int = 640,
        width_multiple: float = 0.50,
        depth_multiple: float = 0.33,
        conf_threshold: float = 0.5
    ):
        super().__init__()

        self.num_classes = num_classes
        self.img_size = img_size
        self.conf_threshold = conf_threshold
        self.strides = self.STRIDES

        # 默认 anchors (像素单位)
        if anchors is None:
            anchors = [
                [(10, 13), (16, 30), (33, 23)],
                [(30, 61), (62, 45), (59, 119)],
                [(116, 90), (156, 198), (373, 326)]
            ]

        # 注册 anchor grid (归一化到 grid 单位)
        self._raw_anchors = anchors

        # Backbone
        self.backbone = CSPDarknet(
            in_channels=3,
            width_multiple=width_multiple,
            depth_multiple=depth_multiple
        )

        # Neck
        backbone_channels = self.backbone.out_channels
        self.neck = PANet(
            in_channels=backbone_channels,
            width_multiple=width_multiple,
            depth_multiple=depth_multiple
        )

        # Head
        neck_channels = self.neck.out_channels
        self.detect = Detect(
            num_classes=num_classes,
            anchors=anchors,
            in_channels=neck_channels
        )

        self.num_anchors = self.detect.num_anchors

    def forward(self, x: torch.Tensor) -> List[torch.Tensor]:
        """
        前向传播

        Args:
            x: (B, 3, H, W)

        Returns:
            List of (B, num_anchors, grid_h, grid_w, 5+num_classes) per scale
        """
        # Backbone
        features = self.backbone(x)

        # Neck
        features = self.neck(features)

        # Detect
        outputs = self.detect(list(features))

        return outputs

    @torch.no_grad()
    def predict(
        self,
        x: torch.Tensor,
        conf_threshold: Optional[float] = None,
        device: Optional[torch.device] = None
    ) -> List[List[Dict]]:
        """
        预测并解码边界框 (向量化)

        Args:
            x: (B, 3, H, W)
            conf_threshold: 置信度阈值

        Returns:
            batch_predictions: 每张图像的检测结果列表
        """
        if conf_threshold is None:
            conf_threshold = self.conf_threshold
        if device is None:
            device = x.device

        self.eval()
        outputs = self.forward(x)

        img_h, img_w = x.shape[2:]

        return self._decode_multi_scale(outputs, conf_threshold, device, img_h, img_w)

    def _decode_multi_scale(
        self,
        outputs: List[torch.Tensor],
        conf_threshold: float,
        device: torch.device,
        img_h: int,
        img_w: int
    ) -> List[List[Dict]]:
        """
        多尺度预测解码
        """
        B = outputs[0].shape[0]
        all_boxes = [[] for _ in range(B)]

        anchors = self.detect.anchors  # (num_layers, num_anchors, 2)

        for layer_idx, output in enumerate(outputs):
            # output: (B, na, H, W, 5+nc)
            _, na, H, W, _ = output.shape
            stride = self.strides[layer_idx]

            # 构建 grid
            grid_y, grid_x = torch.meshgrid(
                torch.arange(H, device=device),
                torch.arange(W, device=device),
                indexing='ij'
            )
            grid_x = grid_x.view(1, 1, H, W)
            grid_y = grid_y.view(1, 1, H, W)

            # anchor 尺寸 (转为 grid 单位)
            anchor_grid = anchors[layer_idx].view(1, na, 1, 1, 2).to(device)
            anchor_w = anchor_grid[..., 0] / stride  # (1, na, 1, 1)
            anchor_h = anchor_grid[..., 1] / stride

            # 解码
            tx = output[..., 0]
            ty = output[..., 1]
            tw = output[..., 2]
            th = output[..., 3]
            obj = output[..., 4]
            cls = output[..., 5:]

            # YOLOv5 解码公式
            bx = (torch.sigmoid(tx) * 2 - 0.5 + grid_x) * stride
            by = (torch.sigmoid(ty) * 2 - 0.5 + grid_y) * stride
            bw = (torch.sigmoid(tw) * 2) ** 2 * anchor_w.unsqueeze(-1).squeeze(-1) * stride
            bh = (torch.sigmoid(th) * 2) ** 2 * anchor_h.unsqueeze(-1).squeeze(-1) * stride

            obj_conf = torch.sigmoid(obj)
            cls_conf = torch.sigmoid(cls)
            max_cls_conf, cls_id = cls_conf.max(dim=-1)

            final_conf = obj_conf * max_cls_conf

            # 转为 xyxy
            x1 = (bx - bw / 2).clamp(0, img_w)
            y1 = (by - bh / 2).clamp(0, img_h)
            x2 = (bx + bw / 2).clamp(0, img_w)
            y2 = (by + bh / 2).clamp(0, img_h)

            mask = final_conf > conf_threshold

            for b in range(B):
                b_mask = mask[b]
                if not b_mask.any():
                    continue

                dets = []
                cur_x1 = x1[b][b_mask]
                cur_y1 = y1[b][b_mask]
                cur_x2 = x2[b][b_mask]
                cur_y2 = y2[b][b_mask]
                cur_conf = final_conf[b][b_mask]
                cur_cls = cls_id[b][b_mask]

                for k in range(cur_conf.size(0)):
                    dets.append({
                        'class_id': cur_cls[k].item(),
                        'confidence': cur_conf[k].item(),
                        'bbox': (cur_x1[k].item(), cur_y1[k].item(),
                                 cur_x2[k].item(), cur_y2[k].item())
                    })
                all_boxes[b].extend(dets)

        return all_boxes

    def get_config(self) -> Dict:
        """获取模型配置"""
        return {
            'num_classes': self.num_classes,
            'anchors': self._raw_anchors,
            'img_size': self.img_size,
            'strides': self.strides,
            'num_anchors': self.num_anchors,
            'conf_threshold': self.conf_threshold,
        }


# ============ 工厂函数 ============

def _create_yolov5(
    variant: str,
    num_classes: int = 80,
    img_size: int = 640,
    anchors: Optional[List] = None
) -> YOLOv5:
    """创建指定变体的 YOLOv5"""
    configs = {
        'n': (0.25, 0.33),
        's': (0.50, 0.33),
        'm': (0.75, 0.67),
        'l': (1.00, 1.00),
        'x': (1.25, 1.33),
    }
    width, depth = configs[variant]
    return YOLOv5(
        num_classes=num_classes,
        anchors=anchors,
        img_size=img_size,
        width_multiple=width,
        depth_multiple=depth
    )


def create_yolov5(
    num_classes: int = 80,
    img_size: int = 640,
    variant: str = 's',
    pretrained: bool = False
) -> YOLOv5:
    """
    创建 YOLOv5 模型的工厂函数

    Args:
        num_classes: 类别数
        img_size: 输入图像尺寸
        variant: 模型变体 ('n', 's', 'm', 'l', 'x')
        pretrained: 是否加载预训练权重

    Returns:
        model: YOLOv5 模型
    """
    model = _create_yolov5(variant, num_classes, img_size)

    if pretrained:
        print("Warning: Pretrained weights not available yet")

    return model


if __name__ == '__main__':
    print("Testing YOLOv5...")

    for variant in ['n', 's', 'm', 'l']:
        model = create_yolov5(num_classes=80, variant=variant)
        x = torch.randn(1, 3, 640, 640)
        outputs = model(x)

        total_params = sum(p.numel() for p in model.parameters())
        print(f"\nYOLOv5{variant}:")
        print(f"  Parameters: {total_params:,} ({total_params * 4 / 1e6:.1f} MB)")
        for i, out in enumerate(outputs):
            print(f"  Scale {i} (stride={model.strides[i]}): {out.shape}")

    # 测试预测
    print("\nTesting predict...")
    model = create_yolov5(num_classes=80, variant='s')
    x = torch.randn(2, 3, 640, 640)
    preds = model.predict(x, conf_threshold=0.5)
    for i, p in enumerate(preds):
        print(f"  Image {i}: {len(p)} detections")

    print("\nAll tests passed!")
