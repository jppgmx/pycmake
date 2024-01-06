#
#   pycmake Options
#
#   Copyright (c) 2023 jppgmx
#   Licensed under MIT License
#

from abc import ABC, abstractmethod
from cmake.cbasic import CMakeValType, CMakeValue

class CMakeInitOptions:
    enableLogging: bool
    logFile: str
    cmakePath: str
    skipTest: bool

    def __init__(self, enableLogging: bool = False, logFile: str = 'pycmake.log', cmakePath: str = None, skipTest: str = False) -> None:
        self.enableLogging = enableLogging
        self.logFile = logFile
        self.cmakePath = cmakePath
        self.skipTest = skipTest

class CMakeBaseOption(ABC):
    name: str
    cmdOption: str
    format: str
    type: CMakeValType

    default: CMakeValue = None

    def __init__(self, name: str, cmd: str, format: str, type: CMakeValType, default: str | bool | dict[str, CMakeValue]):
        self.name = name
        self.cmdOption = cmd
        self.format = format
        self.type = type
        self.default = CMakeValue(default)

    @abstractmethod
    def compile(self, value: CMakeValue) -> str | list[str]:
        pass

class CMakeSimpleOption(CMakeBaseOption):

    def compile(self, value: CMakeValue) -> str | list[str]:
        val = value

        if value == None:
            val = self.default

        valStr = str(val.value).upper() if val.type == CMakeValType.BOOL else f'"{str(val.value)}"'
        ssep = '<#-nl-#>'

        optString = self.format.format(
            option=self.cmdOption,
            type=self.type.name.upper(),
            value=valStr,
            ssp=ssep
            )

        if ssep in optString:
            return optString.split('<#-nl-#>')

        return optString
    
class CMakeOptionalSimpleOption(CMakeSimpleOption):
    def __init__(self, name: str, cmd: str, format: str, type: CMakeValType):
        super().__init__(name, cmd, format, type, None)

    def compile(self, value: CMakeValue) -> str | list[str]:
        if self.value == None:
            return []
        return super().compile(value)
    
class CMakeVariablesOption(CMakeBaseOption):
    def __init__(self, remove = False):
        if remove:
            super().__init__('remove_vars', '-U', '{option}{varname}', CMakeValType.VARDICT, {})
        else:
            super().__init__('variables', '-D', '{option}{varname}:{type}={value}', CMakeValType.VARDICT, {})

    def compile(self, value: CMakeValue) -> str | list[str]:
        
        vars = []
        if value == None:
            return vars
        
        if value.type != CMakeValType.VARDICT:
            raise ValueError('Invalid value: ' + value.value)

        for key, val in value.value.items():
            if val == None and self.cmdOption == '-U':
                val = ''
            else:
                raise ValueError(f'Variable {key} is empty!')

            valStr = str(val.value).upper() if val.type == CMakeValType.BOOL else f'"{str(val.value)}"'

            vars.append( self.format.format(
                option=self.cmdOption,
                varname=key.upper(),
                type=val.type.name.upper(),
                value=valStr
            ) )

        return vars
    
class CMakeSwitchOption(CMakeSimpleOption):
    def __init__(self, name: str, cmd: str, default: bool):
        super().__init__(name, cmd, '{option}', CMakeValType.BOOL, default)

    def compile(self, value: CMakeValue) -> str | list[str]:
        if value.type != CMakeValType.BOOL:
            return []
        
        if value.value == False:
            return []

        return super().compile(value)


class CMakeRawOptions:
    """
    NOTE: If there is an option that has a space between it and the value, put the option followed by a SEPARATE value!

    Example:
        cmake ... --foo Bar

        Wrong:
            ['--foo Bar']

        Correct:
            ['--foo', 'Bar']
    """
    args: list[str]

    def __init__(self, args: list[str] = []) -> None:
        if self.args == None:
            self.args = []
        
        for arg in args:
            if arg == None:
                continue
            if arg == '':
                continue

            self.args.append(arg)