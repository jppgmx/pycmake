#
#   Windows Kernel32 Basic Implementation
#
#   Copyright (C) 2023 Jppgmx
#   Licensed under MIT License
#
import cmakeutils.platcheck as pc
import cmakeutils.logging as lg

import ctypes as ct
import ctypes.wintypes as wt

import os.path as ph

from . import winconstants as wc
from . import winerror as werr

AllocOptions = wc._AllocOptions
FormatOptions = wc._FormatOptions
FormatSource = wc._FormatSource
SearchMode = wc._SearchMode

ErrCodes = werr._Win32ErrorCodes

def LocalAlloc(sizeInBytes: wc.SIZE_T, options: AllocOptions = [AllocOptions.AL_FIXED, AllocOptions.AL_ZEROINIT]) -> wt.HLOCAL:
    if sizeInBytes <= 0:
        raise ct.WinError(ErrCodes.ERROR_INVALID_PARAMETER, 'Invalid parameter.')
    
    localalloc = __GetKernel32().LocalAlloc
    localalloc.argtypes = [
        wt.UINT,
        wc.SIZE_T
    ]
    localalloc.restype = wt.HLOCAL

    flags = wt.UINT(0)
    for fl in options:
        flags |= fl

    wl.logprint_func(localalloc, [flags, sizeInBytes])
    return localalloc(flags, sizeInBytes)

def LocalFree(ptr: wt.HLOCAL) -> wt.HLOCAL:
    localfree = __GetKernel32().LocalFree
    localfree.argtypes = [
        wt.HLOCAL
    ]

    localfree.restype = wt.HLOCAL

    return localfree(ptr)

def FormatMessage(source: FormatSource, srcInput: (str | ct.WinDLL) = None, code: wt.DWORD = 0, lang: wt.DWORD = 0, args: list[str] = []) -> str:
    formatmsg = __GetKernel32().FormatMessageW
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
    lpcSource: wt.LPCVOID | wt.LPWSTR = wt.LPCVOID()
    dwCode: wt.DWORD = code
    dwLang: wt.DWORD = lang
    dwSize: wt.DWORD = 0

    buffer: wt.LPWSTR = wt.LPWSTR()
    lpBuffer: wt.LPWSTR = ct.cast( ct.byref(buffer), wt.LPWSTR )

    vaList: wc.LPVALIST = wc.LPVALIST()
    
    # Set the corresponding flags

    # If the Source is System:
    #   From System + Alloc Buffer + Ignore Inserts (Formatation)
    if source == FormatSource.FS_SYSTEM:
        flags = FormatOptions.FO_ALLOC_BUFFER | FormatOptions.FO_IGNORE_INSERTS | source

    # If the Source is Module:
    #   From Module (use srcInput) + Alloc Buffer + Ignore Inserts (Formatation)
    elif source == FormatSource.FS_HMODULE:
        flags = FormatOptions.FO_ALLOC_BUFFER | FormatOptions.FO_IGNORE_INSERTS | source

    # If the Source is String:
    #   From String (use srcInput) + Alloc Buffer + Use array of arguments (aka DWORD_PTR[]) instead of va_list*
    elif source == FormatSource.FS_STRING:
        flags = FormatOptions.FO_ALLOC_BUFFER | FormatOptions.FO_VALUEARR_INSTEAD_VALIST | source

    else:
        raise ct.WinError(ErrCodes.ERROR_INVALID_PARAMETER, 'Invalid parameter.')
    
    # Configure source
    if source == FormatSource.FS_HMODULE:
        if not type(srcInput) is ct.WinDLL:
            raise ValueError('Expected a WinDLL at srcInput.')
        
        lpcSource = wt.LPCVOID(srcInput._handle)
        
    elif source == FormatSource.FS_STRING:
        if not type(srcInput) is str:
            raise ValueError('Expected a str at srcInput.')
        
        lpcSource = wt.LPWSTR(srcInput)

        #Configure argument array
        _vaList_wstr = [ wt.LPCWSTR(arg) for arg in args ]
        _vaList_ptr = [ ct.cast(wstr, wt.LPCVOID) for wstr in _vaList_wstr ]
        _vaList_dwptr = [ wc.DWORD_PTR( ptr.value ) for ptr in _vaList_ptr ]
        _vaList_arr = (wc.DWORD_PTR * len(_vaList_dwptr))(*_vaList_dwptr)
        vaList = ct.cast(_vaList_arr, wc.LPVALIST)

    result = formatmsg(
        flags,
        lpcSource,
        dwCode,
        dwLang,
        lpBuffer,
        dwSize,
        vaList
    )

    if result == ErrCodes.ERROR_SUCCESS.value:
        code = GetLastError()
        raise ct.WinError(code, FormatMessage(FormatSource.FS_SYSTEM, code=code))
    
    msg = str(buffer.value)
    LocalFree(buffer)

    return msg

def GetLastError() -> wt.DWORD:
    getlasterror = __GetKernel32().GetLastError
    getlasterror.argtypes = []
    getlasterror.restype = wt.DWORD
    return getlasterror()

def SetSearchPathMode(mode: SearchMode) -> wt.BOOL:
    set_search_path_mode = __GetKernel32().SetSearchPathMode

    set_search_path_mode.argtypes = [
        wt.DWORD
    ]

    set_search_path_mode.restype = wt.BOOL

    dwMode = wt.DWORD(mode)
    result: wt.BOOL = set_search_path_mode(dwMode)
    dwCode = GetLastError()

    if result != 0:
        return True

    ct.WinError(dwCode, FormatMessage(FormatSource.FS_SYSTEM, code=dwCode))

def SearchPath(fileName: str, ext: str = None, path: str = None) -> tuple[str, str]:
    lpPath = wt.LPCWSTR(path)
    lpFileName = wt.LPCWSTR(fileName)
    lpExtension = wt.LPCWSTR(ext)

    bufferLen: wt.DWORD = wc.MAX_PATH
    buffer = ct.create_unicode_buffer('', bufferLen)
    
    filePart: wt.LPWSTR = wt.LPWSTR()
    lpFilePart = ct.byref(filePart)

    search = __GetKernel32().SearchPathW
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
        lpPath,
        lpFileName,
        lpExtension,
        bufferLen,
        buffer,
        lpFilePart
    )

    if result == 0:
        dwCode = GetLastError()
        raise ct.WinError(dwCode, FormatMessage(FormatSource.FS_SYSTEM, code=dwCode))
    
    _filePath = (buffer.value, filePart.value)
    return _filePath

def __GetKernel32() -> ct.WinDLL:
    if not pc.isWindows():
        raise OSError('Cannot use Kernel32 in a different system!')

    return ct.windll.kernel32