"""
PANet Neck for YOLOv5
Feature Pyramid Network (FPN) + Path Aggregation Network (PAN)
"""

import torch
import torch.nn as nn
from typing import Tuple
from .layers import Conv, C3, Concat


class PANet(nn.Module):
    """
    PANet Neck: FPN (自顶向下) + PAN (自底向上)

    结构:
        P5 (1/32) ──┐
                     ↓ upsample + concat
        P4 (1/16) ──→ FPN_P4 ──┐
                     ↓ upsample + concat
        P3 (1/8)  ──→ FPN_P3 ──→ PAN_P3 (output)
                                  ↓ downsample + concat
                     FPN_P4 ──→ PAN_P4 (output)
                                  ↓ downsample + concat
                     P5 ──────→ PAN_P5 (output)
    """

    def __init__(
        self,
        in_channels: Tuple[int, int, int] = (256, 512, 1024),
        width_multiple: float = 0.50,
        depth_multiple: float = 0.33
    ):
        super().__init__()

        c3, c4, c5 = in_channels

        def ch(c):
            return max(round(c * width_multiple / 8) * 8, 8)

        def depth(n):
            return max(round(n * depth_multiple), 1)

        # 实际使用缩放后的通道数
        c3, c4, c5 = in_channels  # 已经缩放过

        # ============ FPN (自顶向下) ============

        # P5 -> P4
        self.lateral_p5 = Conv(c5, c4, 1, 1)
        self.upsample = nn.Upsample(scale_factor=2, mode='nearest')
        self.fpn_c3_p4 = C3(c4 + c4, c4, depth(3), shortcut=False)

        # P4 -> P3
        self.lateral_p4 = Conv(c4, c3, 1, 1)
        self.fpn_c3_p3 = C3(c3 + c3, c3, depth(3), shortcut=False)

        # ============ PAN (自底向上) ============

        # P3 -> P4
        self.down_conv_p3 = Conv(c3, c3, 3, 2)
        self.pan_c3_p4 = C3(c3 + c4, c4, depth(3), shortcut=False)

        # P4 -> P5
        self.down_conv_p4 = Conv(c4, c4, 3, 2)
        self.pan_c3_p5 = C3(c4 + c5, c5, depth(3), shortcut=False)

        # Concat
        self.concat = Concat(dim=1)

        # 保存输出通道数
        self.out_channels = (c3, c4, c5)

    def forward(
        self,
        features: Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Args:
            features: (p3, p4, p5) 来自 backbone

        Returns:
            out_p3: 小目标检测特征 (stride=8)
            out_p4: 中目标检测特征 (stride=16)
            out_p5: 大目标检测特征 (stride=32)
        """
        p3, p4, p5 = features

        # ============ FPN 自顶向下 ============

        # P5 上采样 + P4 融合
        fpn_p4 = self.concat([self.upsample(self.lateral_p5(p5)), p4])
        fpn_p4 = self.fpn_c3_p4(fpn_p4)

        # P4 上采样 + P3 融合
        fpn_p3 = self.concat([self.upsample(self.lateral_p4(fpn_p4)), p3])
        fpn_p3 = self.fpn_c3_p3(fpn_p3)

        # ============ PAN 自底向上 ============

        # P3 下采样 + FPN_P4 融合
        pan_p4 = self.concat([self.down_conv_p3(fpn_p3), fpn_p4])
        pan_p4 = self.pan_c3_p4(pan_p4)

        # P4 下采样 + P5 融合
        pan_p5 = self.concat([self.down_conv_p4(pan_p4), p5])
        pan_p5 = self.pan_c3_p5(pan_p5)

        return fpn_p3, pan_p4, pan_p5


if __name__ == '__main__':
    print("Testing PANet...")

    # 模拟 backbone 输出 (YOLOv5s)
    def ch(c):
        return max(round(c * 0.50 / 8) * 8, 8)

    c3, c4, c5 = ch(256), ch(512), ch(1024)
    p3 = torch.randn(1, c3, 80, 80)
    p4 = torch.randn(1, c4, 40, 40)
    p5 = torch.randn(1, c5, 20, 20)

    neck = PANet(
        in_channels=(c3, c4, c5),
        width_multiple=0.50,
        depth_multiple=0.33
    )

    out_p3, out_p4, out_p5 = neck((p3, p4, p5))
    print(f"P3: {p3.shape} -> {out_p3.shape}")
    print(f"P4: {p4.shape} -> {out_p4.shape}")
    print(f"P5: {p5.shape} -> {out_p5.shape}")

    params = sum(p.numel() for p in neck.parameters())
    print(f"Parameters: {params:,}")

    print("\nAll tests passed!")
