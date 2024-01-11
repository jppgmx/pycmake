#
#   pycmake Setup
#
#   Copyright (C) 2023 jppgmx
#   Licensed under MIT License
#

from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    description = fh.read()

setup(
    name='pycmake',
    version='0.0.1',
    author='jppgmx',
    author_email='',
    packages=find_packages(exclude='tests'),
    description='CMake automation!',
    long_description=description,
    long_description_content_type='text/markdown',
    url='https://github.com/jppgmx/pycmake',
    license='MIT',
    python_requires='>=3.8',
    install_requires=[]
)
