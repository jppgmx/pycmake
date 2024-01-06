#
#   pycmake CMake Instance
#
#   Copyright (C) 2023 jppgmx
#   Licensed under MIT License
#

import cmake.ccmd as cc
import subprocess as sp
import os
import random

from abc import ABC, abstractmethod
from threading import Thread

from cmakeutils import logging as internal_logger

from cmake.options import CMakeRawOptions

class _cmakeworker(ABC):
    id: int

    def __init__(self):
        self.id = random.randint(1, 999)

    @abstractmethod
    def onProcess(self, totalLines: list[str], currentLn: str):
        pass

    @abstractmethod
    def onError(self, totalLines: list[str], currentLn: str):
        pass

    @abstractmethod
    def onWarn(self, totalLines: list[str], currentLn: str):
        pass

    @abstractmethod
    def returnCode(self, code: int):
        pass

class _cmakeinst:
    """
    Represents an instance of cmake.
    Note: attributes with a "scope" prefix are used PER CALL, i.e. after an invoke call, they are reset.
    """

    executablePath: str = None
    environ: dict[str, str] = None
    version: str

    scopeWorkers: list[_cmakeworker] = []
    scopeEnviron: dict[str, str] = {}
    scopePaths: list[str] = []
    
    def __init__(self, executablePath: str, version: str):
        self.executablePath = executablePath
        self.environ = os.environ
        self.version = version

    def invoke(self, command: cc.CMakeCommand, rawArgs: CMakeRawOptions = CMakeRawOptions()):
        args: list[str] = None
        
        internal_logger.log('Validating arguments...')
        command.validate()
        args = [self.executablePath]
        args += command.compile()
        args += rawArgs.args

        env = {**self.environ, **(self.scopeEnviron if self.scopeEnviron != None else {})}

        spaths = self.scopePaths if self.scopePaths != None else []
        newPaths = f'{env['PATH']}{os.pathsep}{os.pathsep.join(spaths)}'
        env['PATH'] = newPaths
        internal_logger.log('Invoking cmake executable with arguments: \n[\n    ' + '\n    '.join(args) + '\n]')
        proc = sp.Popen(
            args, bufsize=1, stdout=sp.PIPE, stderr=sp.PIPE, env=env
        )

        stdthreadname = 'pycmake Thread Processor #' + str(random.randint(1, 99))
        stdprocessor = Thread(
            name=stdthreadname,
            args=[proc, self.scopeWorkers, stdthreadname],
            daemon=True,
            target=self._doProcessOutputs
        )

        internal_logger.log('Starting ' + stdprocessor.name + ' and waiting executable finishes...')
        stdprocessor.start()
        proc.wait()
        stdprocessor.join()

        internal_logger.log('Cleaning workers...')
        self.scopeWorkers.clear()

        internal_logger.log('Cleaning environ...')
        self.scopeWorkers.clear()

        internal_logger.log('Cleaning paths...')
        self.scopePaths.clear()

        return self

    def registerWorker(self, worker: _cmakeworker):
        if self.scopeWorkers == None:
            self.scopeWorkers = []

        existingWorker = list(
            filter(
                lambda wk: wk.id == worker.id, self.scopeWorkers
            )
        )
        
        if len(existingWorker) == 0:
            internal_logger.log(f'Registering a new worker (id {worker.id})')
            self.scopeWorkers.append(worker)
            return self

        internal_logger.log(f'Worker (id {worker.id}) already registered!', internal_logger.WARN)

        return self

    def appendEnvVariables(self, envArgs: dict[str, str] = {}):
        if envArgs == None:
            return self
        if self.scopeEnviron == None:
            self.scopeEnviron = {}


        for key, val in envArgs.items():
            if key.lower() == 'PATH'.lower():
                raise ValueError('Not allowed: ' + key)

            self[key] = val

        return self
    
    def appendPaths(self, paths: list[str] = []):
        if paths == None:
            return self
        if self.scopePaths == None:
            self.scopePaths = []

        toAdd = []

        for path in paths:
            for spath in self.scopePaths:
                if path.lower() != spath.lower():
                    toAdd.append(path)

        self.scopePaths += toAdd

        return self

    def _doProcessOutputs(self, process: sp.Popen, workers, name):

        stdoutLines = []
        stderrLines = []

        internal_logger.log(f'({name}) -> Listening output...')

        stdoutLines = process.stdout.readlines()
        stderrLines = process.stderr.readlines()

        outIter = iter(stdoutLines)
        errIter = iter(stderrLines)

        while (outLine := next(outIter, None)) != None or (errLine := next(errIter, None)) != None:

            if outLine == None:
                outLine = b''
            if errLine == None:
                errLine = b''
            
            if outLine != b'':
                internal_logger.log(f'({name}) -> {str(outLine)}')
            if errLine != b'':
                internal_logger.log(f'({name}) -> {str(errLine)}')

            for wk in (workers if workers != None else []):
                if outLine != b'':
                    out = str(outLine)

                    wk.onProcess(stdoutLines, out)

                if errLine != b'':
                    err = str(errLine)

                    onLevel = wk.onError if err.startswith('CMake Error:') else wk.onWarn
                    onLevel(stderrLines, err)

        internal_logger.log(f'({name}) -> Process ended with code {process.returncode}')
        for wk in (workers if workers != None else []):
            wk.returnCode(process.returncode)

        stdoutLines.clear()
        stderrLines.clear()


__defaultCmake__: _cmakeinst = None