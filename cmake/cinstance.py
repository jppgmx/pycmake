"""
   pycmake CMake Instance

   Copyright (C) 2023 jppgmx
   Licensed under MIT License

   The module defines all the logic for using cmake.
"""

from abc import ABC, abstractmethod
from threading import Thread

import subprocess as sp
import os
import random
import cmake.ccmd as cc

from cmakeutils import logging as internal_logger

from cmake.coptions import CMakeRawOptions

class CMakeWorker(ABC):
    """
        Represents a listener to receive events during cmake invocation.
    """

    id: int

    def __init__(self):
        self.id = random.randint(1, 999)

    @abstractmethod
    def onprocess(self, totallines: list[str], currentln: str):
        """
            Gets the current line and all lines from stdout.
        """

    @abstractmethod
    def retcode(self, code: int):
        """
            Gets the executable's return code.
        """

class CMakeInst:
    """
    Represents an instance of cmake.
    Note: attributes with a "scope" prefix are used PER CALL,
        i.e. after an invoke call, they are reset.
    """

    executablepath: str = None
    environ: dict[str, str] = None
    version: str

    scopeworkers: list[CMakeWorker] = []
    scopeenviron: dict[str, str] = {}
    scopepaths: list[str] = []

    def __init__(self, executablepath: str, version: str):
        self.executablepath = executablepath
        self.environ = os.environ
        self.version = version

    def invoke(self, command: cc.CMakeCommand, rawargs: CMakeRawOptions = CMakeRawOptions()):
        """
            Invokes the cmake instance with the specified command.
        """
        args: list[str] = None

        internal_logger.log('Validating arguments...')
        command.validate()
        args = [self.executablepath]
        args += command.compile()
        args += rawargs.args

        env = {**self.environ, **(self.scopeenviron if self.scopeenviron is not None else {})}

        spaths = self.scopepaths if self.scopepaths is not None else []
        newpaths = env['PATH'] + os.pathsep + os.pathsep.join(spaths)
        env['PATH'] = newpaths
        internal_logger.log('Invoking cmake executable with arguments: \n[\n    ' +
                            '\n    '.join(args) + '\n]')

        with sp.Popen(
            args, stdout=sp.PIPE, stderr=sp.STDOUT,
            env=dict(sorted(env.items()))
        ) as proc:
            stdthreadname = 'pycmake Thread Processor #' + str(random.randint(1, 99))
            stdprocessor = Thread(
                name=stdthreadname,
                args=[proc, self.scopeworkers, stdthreadname],
                daemon=True,
                target=self.__doprocess_outputs
            )

            internal_logger.log('Starting ' + stdprocessor.name +
                                ' and waiting executable finishes...')
            stdprocessor.start()
            proc.wait()
            stdprocessor.join()

        internal_logger.log('Cleaning workers...')
        self.scopeworkers.clear()

        internal_logger.log('Cleaning environ...')
        self.scopeenviron.clear()

        internal_logger.log('Cleaning paths...')
        self.scopepaths.clear()

        return self

    def registerworker(self, worker: CMakeWorker):
        """
            Registers a listener for the cmake invocation.
        """

        if self.scopeworkers is None:
            self.scopeworkers = []

        existingworker = list(
            filter(
                lambda wk: wk.id == worker.id, self.scopeworkers
            )
        )

        if len(existingworker) == 0:
            internal_logger.log(f'Registering a new worker (id {worker.id})')
            self.scopeworkers.append(worker)
            return self

        internal_logger.log(f'worker (id {worker.id}) already registered!', internal_logger.WARN)

        return self

    def append_env_variables(self, envargs: dict[str, str] = None):
        """
            Adds extra variables to cmake.
        """

        if envargs is None:
            return self
        if self.scopeenviron is None:
            self.scopeenviron = {}


        for key, val in envargs.items():
            if key.lower() == 'PATH'.lower():
                raise ValueError('Not allowed: ' + key)

            self.scopeenviron[key] = val

        return self

    def appendpaths(self, paths: list[str] = None):
        """
            Adds additional paths to the PATH variable temporarily.
        """

        if paths is None:
            return self
        if self.scopepaths is None:
            self.scopepaths = []

        self.scopepaths += list(
            filter(
                lambda p: p is not None and p != '' and os.path.isdir(p),
                paths
                )
            )

        return self

    def __doprocess_outputs(self, process, workers, name):

        def __keep_reading() -> (bool, str):
            out = process.stdout.readline()
            process.stdout.flush()
            keep = out != b''

            return (keep, out)

        internal_logger.log(f'({name}) -> Listening output...')

        stdoutlines = []

        while (pipe := __keep_reading())[0]:

            outline = (b'' if pipe[1] is None else pipe[1]).decode(
                errors='ignore'
            )

            stdoutlines.append(outline)

            if outline != '':
                internal_logger.log(f'({name}) -> {outline}')

            for wk in (workers if workers is not None else []):
                if outline != '':
                    wk.onprocess(stdoutlines, outline)

        internal_logger.log(f'({name}) -> Process ended with code {process.returncode}')
        for wk in (workers if workers is not None else []):
            wk.retcode(process.returncode)

        stdoutlines.clear()
        process.stdout.close()

__defaultCmake__: CMakeInst = None
