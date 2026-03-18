"""
CSPDarknet53 Backbone for YOLOv5
YOLOv5s 架构的特征提取网络
"""

import torch
import torch.nn as nn
from typing import Tuple
from .layers import Conv, C3, SPPF


class CSPDarknet(nn.Module):
    """
    CSPDarknet Backbone (YOLOv5)

    输出三个尺度的特征图:
        P3: stride=8,  channels=256 (小目标)
        P4: stride=16, channels=512 (中目标)
        P5: stride=32, channels=1024 (大目标)

    架构 (以 640x640 输入为例):
        Input (3, 640, 640)
        -> Conv 6x6 s2 (32, 320, 320)        # Stem (替代 Focus)
        -> Conv 3x3 s2 (64, 160, 160)
        -> C3 x1 (64, 160, 160)
        -> Conv 3x3 s2 (128, 80, 80)
        -> C3 x2 (128, 80, 80)
        -> Conv 3x3 s2 (256, 40, 40)          # P3 output
        -> C3 x3 (256, 40, 40)
        -> Conv 3x3 s2 (512, 20, 20)          # P4 output
        -> C3 x1 (512, 20, 20)
        -> SPPF (512, 20, 20)                 # P5 output

    宽度/深度缩放系数用于控制模型大小:
        - YOLOv5n: width=0.25, depth=0.33
        - YOLOv5s: width=0.50, depth=0.33
        - YOLOv5m: width=0.75, depth=0.67
        - YOLOv5l: width=1.00, depth=1.00
        - YOLOv5x: width=1.25, depth=1.33
    """

    def __init__(
        self,
        in_channels: int = 3,
        width_multiple: float = 0.50,
        depth_multiple: float = 0.33
    ):
        super().__init__()

        # 通道数缩放
        def ch(c):
            return max(round(c * width_multiple / 8) * 8, 8)

        # 深度缩放 (C3 block 的重复次数)
        def depth(n):
            return max(round(n * depth_multiple), 1)

        # 保存输出通道数 (缩放后)
        self.out_channels = (ch(256), ch(512), ch(1024))

        # Stem: 6x6 conv with stride 2 (替代 YOLOv5 早期的 Focus 层)
        self.stem = Conv(in_channels, ch(64), 6, 2, 2)

        # Stage 1: 下采样到 1/4
        self.stage1 = nn.Sequential(
            Conv(ch(64), ch(128), 3, 2),
            C3(ch(128), ch(128), depth(3))
        )

        # Stage 2: 下采样到 1/8 -> P3 特征
        self.stage2 = nn.Sequential(
            Conv(ch(128), ch(256), 3, 2),
            C3(ch(256), ch(256), depth(6))
        )

        # Stage 3: 下采样到 1/16 -> P4 特征
        self.stage3 = nn.Sequential(
            Conv(ch(256), ch(512), 3, 2),
            C3(ch(512), ch(512), depth(9))
        )

        # Stage 4: 下采样到 1/32 -> P5 特征 + SPPF
        self.stage4 = nn.Sequential(
            Conv(ch(512), ch(1024), 3, 2),
            C3(ch(1024), ch(1024), depth(3)),
            SPPF(ch(1024), ch(1024), k=5)
        )

        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        前向传播

        Args:
            x: (B, 3, H, W)

        Returns:
            p3: (B, ch(256), H/8,  W/8)   - 小目标特征
            p4: (B, ch(512), H/16, W/16)  - 中目标特征
            p5: (B, ch(1024), H/32, W/32) - 大目标特征
        """
        x = self.stem(x)       # (B, 64, H/2, W/2)
        x = self.stage1(x)     # (B, 128, H/4, W/4)
        p3 = self.stage2(x)    # (B, 256, H/8, W/8)
        p4 = self.stage3(p3)   # (B, 512, H/16, W/16)
        p5 = self.stage4(p4)   # (B, 1024, H/32, W/32)

        return p3, p4, p5


if __name__ == '__main__':
    print("Testing CSPDarknet...")

    for name, w, d in [('n', 0.25, 0.33), ('s', 0.50, 0.33),
                        ('m', 0.75, 0.67), ('l', 1.00, 1.00)]:
        model = CSPDarknet(width_multiple=w, depth_multiple=d)
        x = torch.randn(1, 3, 640, 640)
        p3, p4, p5 = model(x)
        params = sum(p.numel() for p in model.parameters())
        print(f"YOLOv5{name}: P3={p3.shape}, P4={p4.shape}, P5={p5.shape}, "
              f"Params={params:,}")

    print("\nAll tests passed!")
