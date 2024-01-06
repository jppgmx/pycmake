__package__ = 'cmake'

from . import cmake
from . import options
from . import cbasic
from . import ccmd
from . import cconstants

from cmake.internal import getdefault, testproj
from cmakeutils import logging

import cmakeutils.platcheck as pc
import platform as p

if not pc.isWindows():
    raise NotImplementedError('Not implemented for platform: ' + p.system())

CMake = cmake._cmakeinst
CMakeDefault = cmake.__defaultCmake__

CMakeConfigureCommand = ccmd.CMakeConfigure

CMakeValue = cbasic.CMakeValue
CMakeValueType = cbasic.CMakeValType

CMakeConstants = cconstants

def cminit(options: options.CMakeInitOptions = options.CMakeInitOptions()):
    global CMakeDefault
    if CMakeDefault != None:
        return 

    if options.enableLogging:
        logging.loginit(options.logFile)

    CMakeDefault = getdefault.cmakeGetDefault(options)