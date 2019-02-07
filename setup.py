#!/usr/bin/env python
from distutils.core import setup
from os import path

from setuptools import find_packages

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='pscp',
    version='0.0.3',
    description='Per-session checkpoint using git-stash-create',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Sunyeop Lee',
    author_email='sunyeop97@gmail.com',
    url='https://github.com/qbx2/pscp',
    license='MIT',
    test_suite='tests',
    python_requires='>=3.5',
    packages=find_packages(),
)
