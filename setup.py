#
#   pycmake Setup
#
#   Copyright (C) 2023 jppgmx
#   Licensed under MIT License
#

import setuptools

with open('README.md', 'r') as fh: 
    description = fh.read() 
  
setuptools.setup( 
    name='pycmake', 
    version='0.0.1', 
    author='jppgmx', 
    author_email='', 
    packages=['cmake', 'cmake.utils'], 
    description='CMake automation!', 
    long_description=description, 
    long_description_content_type='text/markdown', 
    url='https://github.com/jppgmx/pycmake', 
    license='MIT', 
    python_requires='>=3.12', 
    install_requires=[] 
) 