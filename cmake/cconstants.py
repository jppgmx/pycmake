"""

    pycmake CMake Constants

    Copyright (C) 2023 jppgmx
    Licensed under MIT License

    Contains some constants that can be used, 
    such as cache variable names.

"""

from enum import Enum

#
#   Variables Names
#
CMAKE_C_COMPILER = 'CMAKE_C_COMPILER'
CMAKE_CXX_COMPILER = 'CMAKE_CXX_COMPILER'
CMAKE_MAKE_PROGRAM = 'CMAKE_MAKE_PROGRAM'
CMAKE_AR = 'CMAKE_AR'
CMAKE_BUILD_TYPE = 'CMAKE_BUILD_TYPE'

class Configuration(Enum):
    """
        Contains some configurations that the project can have. 
        Typical values include Debug, Release, RelWithDebInfo and MinSizeRel, 
        but custom build types can also be defined.
    """

    DEBUG = 'Debug'
    RELEASE = 'Release'
    RELWITHDEBINFO = 'RelWithDebInfo'
    MINSIZEREL = 'MinSizeRel'
