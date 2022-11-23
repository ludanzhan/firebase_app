#!/usr/bin/env python
from setuptools import setup

__version__ = '0.0.1'
__author__ = 'DSCI 551 Project Team'
__author_email__ = 'dougher@usc.edu'

# version numbering convention:
# X.Y.Z, where X is incremented if the change is not backward- compatible,
# Y is incremented for a bug fix, and Z is incremented if the dependencies change.
# Note if X is incremented, Y and Z are reset to 0; if Y is incremented,
# Z is reset to 0.
###

setup(
    name='edfs',
    author=__author__,
    author_email=__author_email__,
    version=__version__,
    description='Emulated Database File Store',
    packages=['edfs'],
    zip_safe=True,
    include_package_data=True,
    install_requires=[
    ],
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3.7'
    ],
    entry_points={
        'console_scripts': [
            'edfs=edfs.main:entrypoint',
        ]
    },
)
