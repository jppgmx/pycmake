#
#   pycmake Get Default Instance
#
#   Copyright (c) 2023 Jppgmx
#   Licensed under MIT License
#

import os

import cmake
from . import testproj as tproj

import re
import tempfile as tmp

from cmakeutils import platcheck as pc, win32, logging as internal_logger
from subprocess import Popen, PIPE

def cmakeGetDefault(options: cmake.options.CMakeInitOptions):

    internal_logger.log('The module will search for the cmake executable according to the current system specifications.')
    default = None

    pathsep = os.pathsep
    sep = os.sep
    execExt = '.exe' if pc.isWindows() else ''
    execName = f'cmake{execExt}'

    internal_logger.log(f"""Specifications collected: 
    System Path Level Separator = {sep}
    System Path List Separator = {pathsep}
    Executable Extension = {execExt}""")
    internal_logger.log(f'The filename will be "{execName}"')
    cmakePath = __internalsearchpath(execName, options.cmakePath)
    internal_logger.log(f'The search was successful and the path to the supposed cmake executable is "{cmakePath}"')

    if (testExecResult := __testExec(cmakePath))[0]:
        default = cmake.CMake(cmakePath, testExecResult[1])

    return default

# Private functions
def __testExec(fl) -> tuple[bool, str]:
    internal_logger.log('Testing file...')
    internal_logger.log('The API and the developers are not responsible if it is malware. ' +
                        'Make sure that the executable to be started is actually from cmake.', internal_logger.WARN)
    proc = Popen(args=[fl, '--version'], stdout=PIPE, stderr=PIPE)
    (out, err) = proc.communicate()
    proc.wait()

    internal_logger.log(f'Return Code: {proc.returncode}')
    if proc.returncode != 0:
        raise RuntimeWarning(f'The executable {fl} returned {proc.returncode}')
        return (False, '')
    
    internal_logger.log('From stdout, processing and acquiring the version...')
    internal_logger.log(f'Stdout below: \n==========<Begin>==========\n{str(out)}\n==========<End>==========')
    stdout = str(out)
    first = stdout.split('\\n')[0]
    firstDigit = re.search(r'\d', first)

    if not firstDigit:
        internal_logger.log('Failed! Expected a number.')
        raise Exception('Could not process the version of cmake.')
    
    beginVersion = first[firstDigit.start():]
    fromProcessVersion = ''

    for c in beginVersion:
        if c.isdigit() or c == '.':
            fromProcessVersion += c
        else: 
            break

    internal_logger.log(f'The cmake version is: {fromProcessVersion}')

    return (True, fromProcessVersion)

def __internalsearchpath(toFind: str, possiblePath: str):
    result = ''

    if pc.isWindows():
        try:
            internal_logger.log('Searching for the executable through the WinApi functions...')

            internal_logger.log('Using SetSearchPathMode function...')
            win32.kernel.SetSearchPathMode(win32.kernel.SearchMode.SAFE_ENABLE)

            internal_logger.log('Using SearchPath function...')

            if possiblePath != None:
                internal_logger.log('Using user specified path to search: ' + possiblePath)
            result = win32.kernel.SearchPath(toFind, path=possiblePath)[0]
        except OSError as err:
            internal_logger.log(f'The search failed, throwing error with exception:\n   {errStr[0]}', internal_logger.ERROR)

            if possiblePath != None:
                internal_logger.log('Make sure the executable is inside of the defined path: ' + possiblePath, internal_logger.INFO)
            paths = os.environ['PATH'].split(os.pathsep)
            errStr = str(err).splitlines()

            
            internal_logger.log('Make sure the executable is inside the PATH system environment variable.', internal_logger.ERROR)
            internal_logger.log(f'The PATH variable contains the following:\n   {'\n   '.join(paths)}')
            raise FileNotFoundError( 'Cannot find cmake executable!', err )
        
    return result
