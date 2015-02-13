#!/usr/bin/env python
from setuptools import setup, find_packages
from katversion import get_version

setup(
    name="katversion",
    version=get_version(),
    description="Provides versioning for python packages",
    author="MeerKAT CAM Team",
    author_email="cam@ska.ac.za",
    packages=find_packages(),
    include_package_data=True,
    scripts=[
        "scripts/kat-get-version.py",
    ],
    url='http://ska.ac.za/',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=["OS Independent"],
    keywords="meerkat kat ska",
    install_requires=[
        "unittest2>=0.5.1",
        "nose>=1.3, <2.0",
    ],
    zip_safe=False,
    # Bitten Test Suite
    test_suite="nose.collector",
    )
