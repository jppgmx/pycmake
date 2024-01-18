"""
   pycmake Get Default Instance

   Copyright (c) 2023 jppgmx
   Licensed under MIT License

   Gets the default cmake instance by searching either the PATH or the user-defined path.
"""
import os
import re

from subprocess import Popen, PIPE
from cmake import coptions
from cmake import cinstance

from cmakeutils import platcheck as pc, win32, logging as internal_logger

def cmake_get_default(_options: coptions.CMakeInitOptions):
    """
        Searches for cmake.
    """

    internal_logger.log('The module will search for the cmake executable' +
                        ' according to the current system specifications.')
    default = None

    pathsep = os.pathsep
    sep = os.sep
    exec_ext = '.exe' if pc.iswindows() else ''
    exec_name = f'cmake{exec_ext}'

    internal_logger.log(f"""Specifications collected:
    System Path Level Separator = {sep}
    System Path List Separator = {pathsep}
    Executable Extension = {exec_ext}""")
    internal_logger.log(f'The filename will be "{exec_name}"')
    cmake_path = __internalsearchpath(exec_name, _options.cmakepath)
    internal_logger.log('The search was successful and the path to' +
                        f' the supposed cmake executable is "{cmake_path}"')

    if (test_exec_result := __testexec(cmake_path))[0]:
        default = cinstance.CMakeInst(cmake_path, test_exec_result[1])

    return default

# Private functions
def __testexec(fl) -> tuple[bool, str]:
    internal_logger.log('Testing file...')
    internal_logger.log('The API and the developers are not responsible if it is malware. ' +
                        'Make sure that the executable to be started is actually from cmake.', 
                        internal_logger.WARN)

    with Popen(args=[fl, '--version'], stdout=PIPE, stderr=PIPE) as proc:
        (out, _) = proc.communicate()
        proc.wait()

    internal_logger.log(f'Return Code: {proc.returncode}')
    if proc.returncode != 0:
        raise RuntimeWarning(f'The executable {fl} returned {proc.returncode}')

    internal_logger.log('From stdout, processing and acquiring the version...')
    internal_logger.log(f'Stdout below: \n==========<Begin>==========\n{str(out)}' +
                        '\n==========<End>==========')
    stdout = str(out)
    first = stdout.split('\\n', maxsplit=1)[0]
    first_digit = re.search(r'\d', first)

    if not first_digit:
        internal_logger.log('Failed! Expected a number.', internal_logger.ERROR)
        raise RuntimeError('Could not process the version of cmake.')

    beginver = first[first_digit.start():]
    from_proc_version = ''

    for c in beginver:
        if c.isdigit() or c == '.':
            from_proc_version += c
        else:
            break

    internal_logger.log(f'The cmake version is: {from_proc_version}')

    return (True, from_proc_version)

def __internalsearchpath(tofind: str, possiblepath: str):
    result = ''

    if pc.iswindows():
        try:
            internal_logger.log('Searching for the executable through the WinApi functions...')

            internal_logger.log('Using SetSearchPathMode function...')
            win32.kernel.SetSearchPathMode(win32.kernel.SearchMode.SAFE_ENABLE)

            internal_logger.log('Using SearchPath function...')

            if possiblepath is not None:
                internal_logger.log('Using user specified path to search: ' + possiblepath)
            result = win32.kernel.SearchPath(tofind, path=possiblepath)[0]
        except OSError as err:
            errstr = str(err).splitlines()

            internal_logger.log('The search failed, throwing error with exception:\n' +
                                f'   {errstr[0]}', internal_logger.ERROR)

            if possiblepath is not None:
                internal_logger.log('Make sure the executable is inside of the defined path: ' +
                                    possiblepath, internal_logger.ERROR)
            paths = os.environ['PATH'].split(os.pathsep)

            internal_logger.log('Make sure the executable is inside the PATH environment variable.',
                                internal_logger.ERROR)
            internal_logger.log('The PATH variable contains the following:\n   ' +
                                '\n   '.join(paths))
            raise err
    else:
        raise RuntimeError('The package is only available for the Windows platform.')

    return result
