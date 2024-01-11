"""
   pycmake Utils Win Kernel32

   Copyright (C) 2023 jppgmx
   Licensed under MIT License
"""

import platform as plat

def iswindows():
    """
        Check if is Windows Platform
    """

    return plat.system().lower() == 'windows'

def isx64():
    """
        Check if is 64-bit machine
    """

    return plat.architecture()[0].lower() == '64bit'

def iswindows64():
    """
        Check if is Windows 64-bit
    """

    return iswindows() and isx64()
