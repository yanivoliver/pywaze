#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "pywaze",
    version = "0.1",
    packages = find_packages(exclude=['tests']),
    install_requires=['requests'],
    entry_points = {
        'console_scripts': [
            'wazeeta = pywaze.ep:main'
        ]
    },
)
