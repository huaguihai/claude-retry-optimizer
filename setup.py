#!/usr/bin/env python3
"""
setup.py - 安装脚本
"""

from setuptools import setup, find_packages
from pathlib import Path

# 读取 README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="claude-retry-optimizer",
    version="1.0.0",
    author="huaguihai",
    author_email="",
    description="优化 Claude Code 重试行为的工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/huaguihai/claude-retry-optimizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "claude-retry-optimizer=claude_retry_optimizer.menu:main",
        ],
    },
)
