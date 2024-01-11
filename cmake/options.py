"""
   pycmake Options

   Copyright (c) 2023 jppgmx
   Licensed under MIT License
"""

from abc import ABC, abstractmethod
from cmake.cbasic import CMakeValType, CMakeValue

class CMakeInitOptions:
    """
        Represents a set of options to be passed when initializing pycmake.
    """

    enablelogging: bool
    logfile: str
    cmakepath: str

    def __init__(self, enablelogging: bool = False,
                logfile: str = 'pycmake.log', cmakepath: str = None) -> None:
        self.enablelogging = enablelogging
        self.logfile = logfile
        self.cmakepath = cmakepath

class CMakeBaseOption(ABC):
    """
        Base class to implement cmake command options.
    """

    name: str
    cmdoption: str
    format: str
    type: CMakeValType

    default: CMakeValue = None

    def __init__(self, name: str, cmd: str, fmt: str,
                 tp: CMakeValType, default: str | bool | dict[str, CMakeValue]):
        self.name = name
        self.cmdoption = cmd
        self.format = fmt
        self.type = tp
        self.default = CMakeValue(default)

    @abstractmethod
    def compile(self, value: CMakeValue) -> str | list[str]:
        """
            Constructs the option with value in the form of a string or a list of strings.
        """

class CMakeSimpleOption(CMakeBaseOption):
    """
        Simple option. Example: -S source
    """

    def compile(self, value: CMakeValue) -> str | list[str]:
        val = value

        if value is None:
            val = self.default

        valstr = str(val.value).upper() if val.type == CMakeValType.BOOL else f'"{str(val.value)}"'
        ssep = '<#-nl-#>'

        optstring = self.format.format(
            option=self.cmdoption,
            type=self.type.name.upper(),
            value=valstr,
            ssp=ssep
            )

        if ssep in optstring:
            return optstring.split('<#-nl-#>')

        return optstring

class CMakeOptionalSimpleOption(CMakeSimpleOption):
    """
        Optional simple option. Example: -A x64
    """

    def __init__(self, name: str, cmd: str, fmt: str, tp: CMakeValType):
        super().__init__(name, cmd, format, type, None)

    def compile(self, value: CMakeValue) -> str | list[str]:
        if self.default is None:
            return []
        return super().compile(value)

class CMakeVariablesOption(CMakeBaseOption):
    """
        CMake configure variables. Example: -DFOO -DBAR ...
    """

    def __init__(self, remove = False):
        if remove:
            super().__init__('remove_vars', '-U', '{option}{varname}', CMakeValType.VARDICT, {})
        else:
            super().__init__('variables', '-D', '{option}{varname}:{type}={value}',
                             CMakeValType.VARDICT, {})

    def compile(self, value: CMakeValue) -> str | list[str]:
        _vars = []
        if value is None:
            return _vars

        if value.type != CMakeValType.VARDICT:
            raise ValueError('Invalid value: ' + value.value)

        for key, val in value.value.items():
            if self.cmdoption == '-U':
                val = ''
            else:
                raise ValueError(f'Variable {key} is empty!')

            valstr = str(val.value).upper() if val.type == CMakeValType.BOOL else f'"{str(val.value)}"'

            vars.append( self.format.format(
                option=self.cmdoption,
                varname=key.upper(),
                type=val.type.name.upper(),
                value=valstr
            ) )

        return vars

class CMakeSwitchOption(CMakeSimpleOption):
    """
        Switch option. Example: --verbose
    """

    def __init__(self, name: str, cmd: str, default: bool):
        super().__init__(name, cmd, '{option}', CMakeValType.BOOL, default)

    def compile(self, value: CMakeValue) -> str | list[str]:
        if value.type != CMakeValType.BOOL:
            return []

        if not value.value:
            return []

        return super().compile(value)


class CMakeRawOptions:
    """
    NOTE: If there is an option that has a space between it and the value,
    put the option followed by a SEPARATE value!

    Example:
        cmake ... --foo Bar

        Wrong:
            ['--foo Bar']

        Correct:
            ['--foo', 'Bar']
    """
    args: list[str]

    def __init__(self, args: list[str] = []) -> None:
        if self.args is None:
            self.args = []

        for arg in args:
            if arg is None:
                continue
            if arg == '':
                continue

            self.args.append(arg)
