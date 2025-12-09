"""
Setup script for OS Dashboard AI Assistant Platform
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="os-dashboard-ai-assistant",
    version="1.0.0",
    author="AI Assistant Platform Team",
    author_email="team@ai-assistant-platform.com",
    description="Advanced Autonomous Workflows with Multi-Source Data Intelligence",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ai-assistant/os-dashboard-platform",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Office/Business",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "coverage>=7.3.2",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "ml": [
            "scikit-learn>=1.3.2",
            "tensorflow>=2.15.0",
            "torch>=2.1.1",
            "transformers>=4.35.2",
        ],
        "cloud": [
            "boto3>=1.34.0",
            "google-cloud-storage>=2.10.0",
            "azure-storage-blob>=12.19.0",
        ],
        "monitoring": [
            "prometheus-client>=0.19.0",
            "structlog>=23.2.0",
            "sentry-sdk>=1.38.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "os-dashboard=src.dashboard.main_interface:main",
            "ai-assistant=src.core.base_agent:main",
            "data-collector=src.intelligence.data_collector:main",
            "content-generator=src.content.generators:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": [
            "templates/*.html",
            "templates/*.xml",
            "assets/*.css",
            "assets/*.js",
            "config/*.yaml",
            "config/*.json",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/ai-assistant/os-dashboard-platform/issues",
        "Source": "https://github.com/ai-assistant/os-dashboard-platform",
        "Documentation": "https://ai-assistant-platform.readthedocs.io/",
        "Funding": "https://github.com/sponsors/ai-assistant",
    },
    keywords=[
        "ai", "assistant", "automation", "dashboard", "data-intelligence", 
        "content-generation", "system-operations", "quality-assurance",
        "concurrent-processing", "deployment", "office-integration"
    ],
    zip_safe=False,
)