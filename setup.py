"""
谱号转换器安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="clef-converter",
    version="1.0.0",
    author="谱号转换器开发团队",
    author_email="support@clef-converter.com",
    description="智能谱号转换器 - 将中音谱号转换为高音谱号",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/clef-converter",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Musicians",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "gpu": ["torch>=2.0.0", "torchvision>=0.15.0"],
        "dev": ["black", "flake8", "mypy", "pytest", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "clef-converter=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["web/templates/*", "web/static/*"],
    },
)
