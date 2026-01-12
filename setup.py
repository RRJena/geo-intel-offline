"""
Setup script for geo_intel_offline package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="geo-intel-offline",
    version="1.0.1",
    description="Production-ready, offline geo-intelligence library for resolving lat/lon to country, ISO codes, continent, and timezone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Geo Intelligence Team",
    url="https://github.com/your-org/geo-intel-offline",
    packages=find_packages(),
    package_data={
        "geo_intel_offline": [
            "data/*.json.gz",  # Only include compressed data files for distribution
        ],
    },
    include_package_data=True,
    zip_safe=False,  # Data files need to be extracted for loading
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies - pure Python
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "mypy>=1.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    entry_points={
        "console_scripts": [
            "geo-intel-build-data=geo_intel_offline.data_builder:main",
        ],
    },
)
