#
#   pycmake Utils Win Kernel32
#
#   Copyright (C) 2023 Jppgmx
#   Licensed under MIT License
#

import platform as plat

def isWindows():
    return plat.system().lower() == 'windows'

def isX64():
    return plat.architecture()[0].lower() == '64bit'

def isWindows64():
    return isWindows() and isX64()