"""
Data loading and processing module
"""

from .datasets import COCODetectionDataset, collate_fn

__all__ = ['COCODetectionDataset', 'collate_fn']
