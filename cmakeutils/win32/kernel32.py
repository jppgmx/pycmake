# pylint: disable-msg=C0103
# pylint: disable-msg=R0914
"""
   Windows Kernel32 Basic Implementation

   Copyright (C) 2023 jppgmx
   Licensed under MIT License

   Implemented functions:

    Local(Alloc/Free),
    FormatMessage,
    GetLastError,
    SetSearchPathMode,
    SearchPath
"""

import ctypes as ct
import ctypes.wintypes as wt

import cmakeutils.platcheck as pc

from . import winconstants as wc
from . import winerror as werr

AllocOptions = wc.AllocOptions
FormatOptions = wc.FormatOptions
FormatSource = wc.FormatSource
SearchMode = wc.SearchMode

ErrCodes = werr.Win32ErrorCodes

def LocalAlloc(sizeinbytes: wc.SIZE_T, options: AllocOptions =
               AllocOptions.AL_FIXED | AllocOptions.AL_ZEROINIT) -> wt.HLOCAL:
    """
        Allocates a certain amount of bytes in memory according to options.
    """

    if sizeinbytes <= 0:
        raise ct.WinError(ErrCodes.ERROR_INVALID_PARAMETER, 'Invalid parameter.')

    localalloc = __getkrnl32().LocalAlloc
    localalloc.argtypes = [
        wt.UINT,
        wc.SIZE_T
    ]
    localalloc.restype = wt.HLOCAL

    flags = wt.UINT(0)
    for fl in options:
        flags |= fl

    return localalloc(flags, sizeinbytes)

def LocalFree(ptr: wt.HLOCAL) -> wt.HLOCAL:
    """
        Free memory allocated from LocalAlloc
    """

    localfree = __getkrnl32().LocalFree
    localfree.argtypes = [
        wt.HLOCAL
    ]

    localfree.restype = wt.HLOCAL

    return localfree(ptr)

def FormatMessage(source: FormatSource, srcinput: (str | ct.WinDLL) = None,
                  code: wt.DWORD = 0, lang: wt.DWORD = 0, args: list[str] = None) -> str:
    """
        Formats a message that can be obtained from different sources,
        whether from the system, a module or a string.
    """

    formatmsg = __getkrnl32().FormatMessageW
    formatmsg.argtypes = [
        wt.DWORD,
        wt.LPCVOID,
        wt.DWORD,
        wt.DWORD,
        wt.LPWSTR,
        wt.DWORD,
        wc.LPVALIST
    ]

    formatmsg.restype = wt.DWORD

    flags: wt.DWORD = 0
    lpc_source: wt.LPCVOID | wt.LPWSTR = wt.LPCVOID()
    dwcode: wt.DWORD = code
    dwlang: wt.DWORD = lang
    dwsize: wt.DWORD = 0

    buffer: wt.LPWSTR = wt.LPWSTR()
    lpbuffer: wt.LPWSTR = ct.cast( ct.byref(buffer), wt.LPWSTR )

    valist: wc.LPVALIST = wc.LPVALIST()

    # Set the corresponding flags

    # If the Source is System:
    #   From System + Alloc Buffer + Ignore Inserts (Formatation)
    if source == FormatSource.FS_SYSTEM:
        flags = FormatOptions.FO_ALLOC_BUFFER | FormatOptions.FO_IGNORE_INSERTS | source

    # If the Source is Module:
    #   From Module (use srcinput) + Alloc Buffer + Ignore Inserts (Formatation)
    elif source == FormatSource.FS_HMODULE:
        flags = FormatOptions.FO_ALLOC_BUFFER | FormatOptions.FO_IGNORE_INSERTS | source

    # If the Source is String:
    #   From String (use srcinput) + Alloc Buffer +
    #    Use array of arguments (aka DWORD_PTR[]) instead of va_list*
    elif source == FormatSource.FS_STRING:
        flags = FormatOptions.FO_ALLOC_BUFFER | FormatOptions.FO_VALUEARR_INSTEAD_VALIST | source

    else:
        raise ct.WinError(ErrCodes.ERROR_INVALID_PARAMETER, 'Invalid parameter.')

    # Configure source
    if source == FormatSource.FS_HMODULE:
        if not isinstance(srcinput, ct.WinDLL):
            raise ValueError('Expected a WinDLL at srcInput.')

        lpc_source = wt.LPCVOID(srcinput._handle)

    elif source == FormatSource.FS_STRING:
        if not isinstance(srcinput, str):
            raise ValueError('Expected a str at srcInput.')

        lpc_source = wt.LPWSTR(srcinput)

        # Configure argument array
        _valist_args = [] if args is None else args
        _valist_wstr = [ wt.LPCWSTR(arg) for arg in _valist_args ]
        _valist_ptr = [ ct.cast(wstr, wt.LPCVOID) for wstr in _valist_wstr ]
        _valist_dwptr = [ wc.DWORD_PTR( ptr.value ) for ptr in _valist_ptr ]
        _valist_arr = (wc.DWORD_PTR * len(_valist_dwptr))(*_valist_dwptr)
        valist = ct.cast(_valist_arr, wc.LPVALIST)

    result = formatmsg(
        flags,
        lpc_source,
        dwcode,
        dwlang,
        lpbuffer,
        dwsize,
        valist
    )

    if result == ErrCodes.ERROR_SUCCESS.value:
        code = GetLastError()
        raise ct.WinError(code, FormatMessage(FormatSource.FS_SYSTEM, code=code))

    msg = str(buffer.value)
    LocalFree(buffer)

    return msg

def GetLastError() -> wt.DWORD:
    """
        Get system last error.
    """

    getlasterror = __getkrnl32().GetLastError
    getlasterror.argtypes = []
    getlasterror.restype = wt.DWORD
    return getlasterror()

def SetSearchPathMode(mode: SearchMode) -> wt.BOOL:
    """
        Set if enable or disable search safe.
    """

    set_search_path_mode = __getkrnl32().SetSearchPathMode

    set_search_path_mode.argtypes = [
        wt.DWORD
    ]

    set_search_path_mode.restype = wt.BOOL

    dwmode = wt.DWORD(mode)
    result: wt.BOOL = set_search_path_mode(dwmode)
    dwcode = GetLastError()

    if result != 0:
        return True

    raise ct.WinError(dwcode, FormatMessage(FormatSource.FS_SYSTEM, code=dwcode))

def SearchPath(filename: str, ext: str = None, path: str = None) -> tuple[str, str]:
    """
        Searches for a file either by the PATH variable or by a user-defined path.
    """

    lppath = wt.LPCWSTR(path)
    lpfilename = wt.LPCWSTR(filename)
    lpextension = wt.LPCWSTR(ext)

    bufferlen: wt.DWORD = wc.MAX_PATH
    buffer = ct.create_unicode_buffer('', bufferlen)

    filepart: wt.LPWSTR = wt.LPWSTR()
    lpfilepart = ct.byref(filepart)

    search = __getkrnl32().SearchPathW
    search.argtypes = [
        wt.LPCWSTR,
        wt.LPCWSTR,
        wt.LPCWSTR,
        wt.DWORD,
        wt.LPWSTR,
        ct.POINTER(wt.LPWSTR)
    ]
    search.restype = wt.DWORD

    result = search(
        lppath,
        lpfilename,
        lpextension,
        bufferlen,
        buffer,
        lpfilepart
    )

    if result == 0:
        dwcode = GetLastError()
        raise ct.WinError(dwcode, FormatMessage(FormatSource.FS_SYSTEM, code=dwcode))

    _filepath = (buffer.value, filepart.value)
    return _filepath

def __getkrnl32() -> ct.WinDLL:
    if not pc.iswindows():
        raise OSError('Cannot use Kernel32 in a different system!')

    return ct.windll.kernel32
