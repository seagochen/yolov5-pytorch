"""
YOLOv5-PyTorch
A clean, modular implementation of YOLOv5 in PyTorch
"""

__version__ = '5.0.0'

from .models import YOLOv5, create_yolov5, CSPDarknet
from .data import datasets
from .utils import loss, general

__all__ = [
    'YOLOv5',
    'create_yolov5',
    'CSPDarknet',
    '__version__'
]
