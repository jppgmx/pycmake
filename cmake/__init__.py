"""
    pycmake cmake package
    ---------------------

    Copyright (C) 2023 jppgmx
    Licensed under MIT License

    This package is the core of pycmake. 
    It contains the cmake instance, commands, options, 
    in addition to the internals that search for the executable.

    It is recommended to use the aliases defined 
    when importing the package instead of using the submodules, 
    they are: cbasic, ccmd, options, cmake, cconstants and the internal getdefault.


"""

import platform as p
import cmakeutils

import cmakeutils.platcheck as pc

from . import cmake
from . import options
from . import cbasic
from . import ccmd
from . import cconstants

from . import internal

if not pc.iswindows():
    raise NotImplementedError('Not implemented for platform: ' + p.system())

CMake = cmake.CMakeInst
CMakeWorker = cmake.CMakeWorker
CMakeInitializeOptions = options.CMakeInitOptions

CMakeConfigureCommand = ccmd.CMakeConfigure
CMakeBuildCommand = ccmd.CMakeBuildCommand
CMakeInstallCommand = ccmd.CMakeInstallCommand

CMakeValue = cbasic.CMakeValue
CMakeValueType = cbasic.CMakeValType
CMakeRawCommandArgs = options.CMakeRawOptions

CMakeConstants = cconstants

def cminit(_options: CMakeInitializeOptions = CMakeInitializeOptions()):
    """
    Initializes the package logic, looking for cmake by default and 
    enabling other functionality through options.

    There are options such as enabling logging within the package and 
    specifying the file where it will be logged and a custom path to cmake.
    """

    if cmake.__defaultCmake__ is not None:
        return

    if _options.enablelogging:
        cmakeutils.logging.loginit(_options.logfile)

    cmake.__defaultCmake__ = internal.getdefault.cmake_get_default(options)

def cmdefault() -> CMake:
    """
    Gets an initialized instance of cmake.
    """

    if cmake.__defaultCmake__ is None:
        raise RuntimeError('CMake not initalized!')

    return cmake.__defaultCmake__
