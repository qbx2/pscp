#!/usr/bin/env python
from distutils.core import setup

from setuptools import find_packages

setup(
    name='pscp',
    version='0.0.0',
    description='Per-session checkpoint using git-stash-create',
    author='Sunyeop Lee',
    author_email='sunyeop97@gmail.com',
    url='https://github.com/qbx2/pscp',
    license='MIT',
    packages=find_packages(),
)