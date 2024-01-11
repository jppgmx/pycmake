"""
   pycmake Logging

   Copyright (c) 2023 jppgmx
   Licensed under MIT License

"""

import logging
import os
import sys

import inspect as ipc

__loggers__: dict[str, logging.Logger] = None
__initialized__: bool = False

INFO     = logging.INFO
WARN     = logging.WARN
ERROR    = logging.ERROR
CRITICAL = logging.CRITICAL
FATAL    = logging.FATAL
DEBUG    = logging.DEBUG

def loginit(logfile: str):
    """
        Starts logging system.
    """

    global __initialized__
    if __initialized__:
        return

    filehandler = logging.FileHandler(logfile, encoding='utf-8')
    filehandler.level = logging.INFO

    fmt = '[%(asctime)s - pycmake API][pkg %(pkgname)s | mod %(name)s][%(levelname)s]: %(message)s'

    logging.basicConfig(
        format=fmt,
        datefmt='%b %d %Y (%H:%M:%S)',
        level=logging.INFO,
        force=True,
        handlers=[
                filehandler
            ]
        )

    global __loggers__
    __loggers__ = {}
    __initialized__ = True
    log('Logging started!')

def log(msg, level: int = INFO, modulefile: str = None):
    """
        Logs pycmake events.
    """

    if not __initialized__:
        return

    module = ipc.stack()[1].filename if modulefile is None else modulefile

    modulename = os.path.basename(module)
    moduleobj = __find_module_from_file(module)
    modulepackage = 'unnamed' if len(moduleobj.__package__) == 0 else moduleobj.__package__

    global __loggers__
    if not modulename in __loggers__:
        # Setup logger
        __loggers__[modulename] = logging.getLogger(modulename)

    logger = __loggers__[modulename]
    logger.log(
        level=level,
        msg=msg,
        extra={
            'pkgname': modulepackage
            }
        )

def __find_module_from_file(modulefile: str):
    for key, value in sys.modules.items():
        if not key in sys.builtin_module_names:
            if hasattr(value, '__file__'):
                if value.__file__ is None:
                    continue
                left = value.__file__.lower()
                right = modulefile.lower()
                if left == right:
                    return value

    return None
