#
#   pycmake Debug Logging
#
#   Copyright (c) 2023 jppgmx
#   Licensed under MIT License
#

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

def loginit(logFile: str):
    global __initialized__
    if __initialized__:
        return

    fileHandler = logging.FileHandler(logFile, encoding='utf-8')
    fileHandler.level = logging.INFO

    logging.basicConfig(
        format='[%(asctime)s - pycmake API][pkg %(pkgname)s | mod %(name)s][%(levelname)s]: %(message)s',
        datefmt='%b %d %Y (%H:%M:%S)',
        level=logging.INFO,
        force=True,
        handlers=[
                fileHandler
            ]
        )
    
    global __loggers__
    __loggers__ = {}
    __initialized__ = True
    log('Logging started!')
    
def log(msg, level: int = INFO, moduleFl: str = None):
    if not __initialized__:
        return

    module = ipc.stack()[1].filename if moduleFl == None else moduleFl

    moduleName = os.path.basename(module)
    moduleObj = _findModuleFromFile(module)
    modulePackage = 'unnamed' if len(moduleObj.__package__) == 0 else moduleObj.__package__

    global __loggers__
    if not moduleName in __loggers__:
        # Setup logger
        __loggers__[moduleName] = logging.getLogger(moduleName)

    logger = __loggers__[moduleName]
    logger.log(
        level=level,
        msg=msg, 
        extra={
            'pkgname': modulePackage
            }
        )
    
def _findModuleFromFile(moduleFile: str):
    for key, value in sys.modules.items():
        if not key in sys.builtin_module_names:
            if hasattr(value, '__file__'):
                if value.__file__ is None:
                    continue
                left = value.__file__.lower()
                right = moduleFile.lower()
                if left == right:
                    return value
        
    return None