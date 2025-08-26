#!/usr/bin/env python3
"""
Personality Matrix (PMX) - The third component of Sam's autonomous AI trilogy.

This package provides persistent personality management for AI systems,
enabling consistent identity across different LLM backends and sessions.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sam-persona",
    version="1.0.0",
    author="Sam AI",
    author_email="sam@aegis.ai",
    description="Personality Matrix for autonomous AI systems",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/bawtL-Labs/aegis-persona-matrix",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=5.0.0",
        ],
        "api": [
            "fastapi>=0.100.0",
            "uvicorn>=0.22.0",
            "pydantic>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sam-pmxd=sam.persona.service:main",
        ],
    },
    include_package_data=True,
    package_data={
        "sam.persona": ["*.json", "*.yaml", "*.yml"],
    },
)