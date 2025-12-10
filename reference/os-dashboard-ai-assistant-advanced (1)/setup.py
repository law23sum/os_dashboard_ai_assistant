"""
Setup script for OS Dashboard AI Assistant
"""
from pathlib import Path
from setuptools import setup, find_packages

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
DOCS_ROOT = REPO_ROOT / "documentation"


def _load_long_description() -> str:
    doc_candidate = DOCS_ROOT / BASE_DIR.relative_to(REPO_ROOT) / "README.md"
    if not doc_candidate.exists():
        doc_candidate = DOCS_ROOT / "README.md"
    return doc_candidate.read_text(encoding="utf-8")


long_description = _load_long_description()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="os-dashboard-ai-assistant",
    version="1.0.0",
    author="OS Dashboard AI Team",
    author_email="contact@example.com",
    description="A comprehensive AI assistant integrating multiple productivity applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/os-dashboard-ai-assistant",
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
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Email",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "dashboard-ai=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
)
