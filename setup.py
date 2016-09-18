#!/usr/bin/env python

from setuptools import setup, find_packages

from ndn.common import VERSION_NUMBER

setup(
    name = "Mini-NDN",
    version = VERSION_NUMBER,
    packages = find_packages(),
    scripts = ['bin/minindn', 'bin/minindnedit'],
)
