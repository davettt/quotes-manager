"""Setup configuration for Quotes Manager."""

from setuptools import find_packages, setup

from version import __author__, __description__, __version__

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip()
        and not line.startswith("#")
        and not line.startswith("black")
        and not line.startswith("ruff")
    ]

# Read long description from README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="quotes-manager",
    version=__version__,
    author=__author__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/quotes-manager",  # Update with actual repo URL
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    include_package_data=True,
    install_requires=requirements,
    py_modules=["main", "version"],
    entry_points={
        "console_scripts": [
            "quotes=main:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
)
