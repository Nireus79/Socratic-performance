"""Setup configuration for socratic-performance"""

from setuptools import setup, find_packages

setup(
    name="socratic-performance",
    version="0.1.2",
    description="Performance monitoring and caching utilities for AI systems",
    author="Socratic Team",
    author_email="team@socratic.dev",
    url="https://github.com/Nireus79/Socratic-performance",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
