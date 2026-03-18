"""
YOLOv5-PyTorch Setup Script
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent

requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='yolov5-pytorch',
    version='5.0.0',
    author='YOLOv5 Contributors',
    description='A clean, modular implementation of YOLOv5 in PyTorch',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'yolov5-train=scripts.train:main',
            'yolov5-detect=scripts.detect:main',
        ],
    },
)
