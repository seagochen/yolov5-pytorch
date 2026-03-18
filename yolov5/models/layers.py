"""
Common layers for YOLOv5
YOLOv5 核心模块：Conv, C3 (CSP Bottleneck), SPPF, Concat
"""

import torch
import torch.nn as nn
from typing import Optional, List


class Conv(nn.Module):
    """
    标准卷积层: Conv2d + BatchNorm + SiLU

    YOLOv5 使用 SiLU (Swish) 替代 LeakyReLU
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 1,
        stride: int = 1,
        padding: Optional[int] = None,
        groups: int = 1,
        act: bool = True
    ):
        super().__init__()
        if padding is None:
            padding = kernel_size // 2

        self.conv = nn.Conv2d(
            in_channels, out_channels,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            groups=groups,
            bias=False
        )
        self.bn = nn.BatchNorm2d(out_channels, eps=1e-3, momentum=0.03)
        self.act = nn.SiLU(inplace=True) if act else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.act(self.bn(self.conv(x)))


class Bottleneck(nn.Module):
    """
    标准瓶颈残差块

    Conv(1x1, c->c_hidden) -> Conv(3x3, c_hidden->c) + shortcut
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        shortcut: bool = True,
        groups: int = 1,
        expansion: float = 0.5
    ):
        super().__init__()
        hidden = int(out_channels * expansion)
        self.cv1 = Conv(in_channels, hidden, 1, 1)
        self.cv2 = Conv(hidden, out_channels, 3, 1, groups=groups)
        self.add = shortcut and in_channels == out_channels

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.cv2(self.cv1(x)) if self.add else self.cv2(self.cv1(x))


class C3(nn.Module):
    """
    CSP Bottleneck with 3 convolutions (YOLOv5 核心模块)

    结构:
        x -> cv1 -> bottlenecks -> cat -> cv3
        x -> cv2 ----------------^
    """
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        n: int = 1,
        shortcut: bool = True,
        groups: int = 1,
        expansion: float = 0.5
    ):
        super().__init__()
        hidden = int(out_channels * expansion)
        self.cv1 = Conv(in_channels, hidden, 1, 1)
        self.cv2 = Conv(in_channels, hidden, 1, 1)
        self.cv3 = Conv(2 * hidden, out_channels, 1, 1)
        self.m = nn.Sequential(
            *(Bottleneck(hidden, hidden, shortcut, groups, expansion=1.0) for _ in range(n))
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.cv3(torch.cat((self.m(self.cv1(x)), self.cv2(x)), dim=1))


class SPPF(nn.Module):
    """
    Spatial Pyramid Pooling - Fast (SPPF)

    使用连续的小kernel MaxPool替代并行大kernel，速度更快效果等价
    3次 5x5 MaxPool 等价于 SPP 中的 5x5, 9x9, 13x13
    """
    def __init__(self, in_channels: int, out_channels: int, k: int = 5):
        super().__init__()
        hidden = in_channels // 2
        self.cv1 = Conv(in_channels, hidden, 1, 1)
        self.cv2 = Conv(hidden * 4, out_channels, 1, 1)
        self.m = nn.MaxPool2d(kernel_size=k, stride=1, padding=k // 2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.cv1(x)
        y1 = self.m(x)
        y2 = self.m(y1)
        return self.cv2(torch.cat((x, y1, y2, self.m(y2)), dim=1))


class Concat(nn.Module):
    """沿指定维度拼接张量"""
    def __init__(self, dim: int = 1):
        super().__init__()
        self.dim = dim

    def forward(self, x: List[torch.Tensor]) -> torch.Tensor:
        return torch.cat(x, dim=self.dim)


if __name__ == '__main__':
    print("Testing YOLOv5 layers...")

    # Conv
    x = torch.randn(2, 64, 32, 32)
    conv = Conv(64, 128, 3, 2)
    y = conv(x)
    print(f"Conv: {x.shape} -> {y.shape}")

    # C3
    x = torch.randn(2, 256, 20, 20)
    c3 = C3(256, 256, n=3)
    y = c3(x)
    print(f"C3: {x.shape} -> {y.shape}")

    # SPPF
    x = torch.randn(2, 1024, 20, 20)
    sppf = SPPF(1024, 1024)
    y = sppf(x)
    print(f"SPPF: {x.shape} -> {y.shape}")

    # Concat
    a = torch.randn(2, 128, 40, 40)
    b = torch.randn(2, 256, 40, 40)
    cat = Concat(dim=1)
    y = cat([a, b])
    print(f"Concat: ({a.shape}, {b.shape}) -> {y.shape}")

    print("\nAll tests passed!")
