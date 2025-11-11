"""Setup script for XPoster."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="xposter",
    version="1.0.0",
    description="Automated X/Twitter posting with personalized writing style learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="XPoster Team",
    author_email="",
    url="https://github.com/yourusername/xposter",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "tweepy>=4.14.0",
        "openai>=1.12.0",
        "anthropic>=0.18.1",
        "tiktoken>=0.6.0",
        "nltk>=3.8.1",
        "spacy>=3.7.4",
        "pandas>=2.2.0",
        "numpy>=1.26.4",
        "python-dotenv>=1.0.1",
        "pyyaml>=6.0.1",
        "schedule>=1.2.1",
        "apscheduler>=3.10.4",
        "sqlalchemy>=2.0.27",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
        "loguru>=0.7.2",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "xposter=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="twitter x automation ai ml writing-style social-media",
)
