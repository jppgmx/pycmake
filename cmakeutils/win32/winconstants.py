"""
   Windows Types and Constants

   Copyright (C) 2023 jppgmx
   Licensed under MIT License
"""

from enum import IntFlag
from sys import maxsize

import ctypes as ct

SIZE_T = ct.c_size_t
VALIST = ct.POINTER( ct.c_char )
LPVALIST = ct.POINTER(VALIST)

DWORD_PTR = ct.c_ulonglong if maxsize > 2**32 else ct.c_uint

MAX_PATH: int = 260

# Options
class SearchMode(IntFlag):
    """
        Set search mode when using SearchPath function.
    """

    SAFE_ENABLE = 0x00000001
    SAFE_DISABLE = 0x00010000

class FormatSource(IntFlag):
    """
        The source that the FormatMessage should use.
    """

    FS_STRING = 0x00000400
    FS_HMODULE = 0x00000800
    FS_SYSTEM = 0x00001000

class FormatOptions(IntFlag):
    """
        Options that FormatMessage uses automatically.
    """

    FO_ALLOC_BUFFER = 0x00000100
    FO_IGNORE_INSERTS = 0x00000200
    FO_VALUEARR_INSTEAD_VALIST = 0x00002000

class AllocOptions(IntFlag):
    """
        Options that LocalAlloc uses to allocate a block of memory.
    """

    AL_ZEROINIT = 0x0040
    AL_MOVEABLE = 0x0002
    AL_FIXED = 0x0000
