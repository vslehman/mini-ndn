#!/usr/bin/env python

from setuptools import setup, find_packages

from minindn.common import VERSION_NUMBER

setup(
    name = "Mini-NDN",
    version = VERSION_NUMBER,
    packages = find_packages(),
    entry_points={
        'console_scripts': [
            'minindn = bin.main:main',
        ],
        'gui_scripts': [
            'minindnedit = bin.minindnedit:main',
        ]
    },
)
