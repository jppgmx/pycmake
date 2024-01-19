"""
   pycmake Options

   Copyright (c) 2023 jppgmx
   Licensed under MIT License
"""
# pylint: disable-msg=W0246
# -> Note: Certain classes based on CMakeBaseOption define __eq__, __ne__ and __hash__ again
#          to be recognized as Hashable types, even if they were defined in the base class.

import dataclasses

from abc import ABC, abstractmethod
from cmake.cbasic import CMakeValType, CMakeValue, castbool

@dataclasses.dataclass
class CMakeInitOptions:
    """
        Represents a set of options to be passed when initializing pycmake.
    """

    enablelogging: bool = False
    logfile: str = 'pycmake.log'
    cmakepath: str = None

@dataclasses.dataclass
class CMakeBaseOption(ABC):
    """
        Base class to implement cmake command options.
    """

    name: str
    cmdoption: str
    format: str
    type: CMakeValType
    default: CMakeValue = None

    @abstractmethod
    def compile(self, value: CMakeValue) -> str | list[str]:
        """
            Constructs the option with value in the form of a string or a list of strings.
        """

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, CMakeBaseOption):
            return False

        return (self.name == __value.name and
                self.cmdoption == __value.cmdoption and self.type == __value.type)

    def __ne__(self, __value: object) -> bool:
        return not self == __value

    def __hash__(self) -> int:
        return hash((self.name, self.cmdoption, self.type))

@dataclasses.dataclass
class CMakeSimpleOption(CMakeBaseOption):
    """
        Simple option. Example: -S source
    """

    def compile(self, value: CMakeValue) -> str | list[str]:
        val = value

        if value is None:
            val = self.default

        valstr = castbool(val.value) if val.type == CMakeValType.BOOL else f'{str(val.value)}'
        ssep = '<#-nl-#>'

        optstring = self.format.format(
            option=self.cmdoption,
            type=self.type.name.upper(),
            value=valstr,
            ssp=ssep,
            q=('"' if ' ' in valstr else '')
            )

        if ssep in optstring:
            return optstring.split('<#-nl-#>')

        return optstring

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value)

    def __ne__(self, __value: object) -> bool:
        return super().__ne__(__value)

    def __hash__(self) -> int:
        return super().__hash__()

@dataclasses.dataclass
class CMakeOptionalSimpleOption(CMakeSimpleOption):
    """
        Optional simple option. Example: -A x64
    """

    def __init__(self, name: str, cmd: str, fmt: str, tp: CMakeValType):
        super().__init__(name, cmd, fmt, tp, None)

    def compile(self, value: CMakeValue) -> str | list[str]:
        if value is None:
            return []
        return super().compile(value)

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value)

    def __ne__(self, __value: object) -> bool:
        return super().__ne__(__value)

    def __hash__(self) -> int:
        return super().__hash__()

@dataclasses.dataclass
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
            _value = val.value
            if self.cmdoption == '-U':
                _value = ''

            if val is None:
                raise ValueError(f'Variable {key} is empty!')
            if val.type == CMakeValType.VARDICT:
                raise ValueError('Invalid value type: VARDICT')

            valstr = castbool(_value) if val.type == CMakeValType.BOOL else f'{_value}'

            _vars.append( self.format.format(
                option=self.cmdoption,
                varname=key.upper(),
                type=val.type.name.upper(),
                value=valstr,
                q=('"' if ' ' in valstr else '')
            ) )

        return _vars

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value)

    def __ne__(self, __value: object) -> bool:
        return super().__ne__(__value)

    def __hash__(self) -> int:
        return super().__hash__()

@dataclasses.dataclass
class CMakeSwitchOption(CMakeSimpleOption):
    """
        Switch option. Example: --verbose
    """

    def __init__(self, name: str, cmd: str, default: bool):
        super().__init__(name, cmd, '{option}', CMakeValType.BOOL, default)

    def compile(self, value: CMakeValue) -> str | list[str]:
        if value is None:
            return []

        if value.type != CMakeValType.BOOL:
            return []

        if not value.value:
            return []

        return super().compile(value)

    def __eq__(self, __value: object) -> bool:
        return super().__eq__(__value)

    def __ne__(self, __value: object) -> bool:
        return super().__ne__(__value)

    def __hash__(self) -> int:
        return super().__hash__()

@dataclasses.dataclass
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
    args: list[str] = None

    def __init__(self, args: list[str] = None) -> None:
        if self.args is None:
            self.args = []
        if args is None:
            return

        for arg in args:
            if arg is None:
                continue
            if arg == '':
                continue

            self.args.append(arg)
