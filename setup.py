#!/usr/bin/env python3
"""
Setup script für den Proxmox Backup Checker.
"""

from setuptools import setup, find_packages
import os

# Lese die README für die lange Beschreibung
def read_readme():
    with open("README.MD", "r", encoding="utf-8") as fh:
        return fh.read()

# Lese die requirements
def read_requirements():
    with open("app/requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="proxmox-backup-checker",
    version="1.0.0",
    author="jokrEZ",
    author_email="",
    description="Intelligente Überwachung von Proxmox VE Backup-Jobs mit Home Assistant Integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jokrEZ/proxmox-backup-checker",
    project_urls={
        "Bug Reports": "https://github.com/jokrEZ/proxmox-backup-checker/issues",
        "Source": "https://github.com/jokrEZ/proxmox-backup-checker",
        "Documentation": "https://github.com/jokrEZ/proxmox-backup-checker#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "bandit>=1.7",
            "safety>=2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "proxmox-backup-checker=app.check_backups:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["config.json.example", "requirements.txt"],
    },
    keywords="proxmox backup monitoring homeassistant automation",
    platforms=["any"],
) 