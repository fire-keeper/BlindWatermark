#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys
 
setup(
    name="BlindWatermark",
    version="0.1.0",
    author="Fire-Keeper",
    author_email="1627517214@qq.com",
    description="using invisible watermark to protect creator's intellectual property",
    # long_description=open("README.rst").read(),
    license="MIT",
    url="https://github.com/fire-keeper/BlindWatermark",
    packages=['BlindWatermark',],
    install_requires=[
        'numpy',
        'opencv'
        ],
    # classifiers=[
    #     "Environment :: Web Environment",
    #     "Intended Audience :: Developers",
    #     "Operating System :: OS Independent",
    #     "Topic :: Utilities",
    #     "Topic :: Software Development :: Libraries :: Python Modules",
    #     "Programming Language :: Python",
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3.5",
    #     "Programming Language :: Python :: 3.6",
    #     "Programming Language :: Python :: 3.7",
    # ],
)
