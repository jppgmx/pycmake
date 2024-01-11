"""
    pycmake cmakeutils module
    --------------------

    Copyright (C) 2023 jppgmx
    Licensed under MIT License

    This module assists the main package by logging, platform checking, and 
    implementing platform functions such as WinAPI.


"""

from . import platcheck as platfrom2
from . import typecheck
from . import logging

if platfrom2.iswindows():
    from . import win32
