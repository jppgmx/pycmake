#
#   pycmake CMake Commands (aka. Configure, Build, Install, ...)
#
#   Copyright (C) 2023 jppgmx
#   Licensed under MIT License
#

from abc import ABC, abstractmethod
from enum import Enum
import os

from cmake.cbasic import CMakeValType, CMakeValue
from cmake import options as ops
from cmake.options import CMakeBaseOption

class CMakeCommand(ABC):

    commandName: str
    __options__: dict[ops.CMakeBaseOption, CMakeValue] = None

    def __init__(self, **kwargs):
        self.__options__ = self.getOptions()

        for key, val in kwargs.items():
            for defOp in self.__options__.keys():
                if key == defOp.name:
                    value = CMakeValue(val)
                    if defOp.type != value.type:
                        raise ValueError(f'Incompatible types between value ({value.type}) and option {defOp.name} ({defOp.type})')
                    self.__options__[defOp] = value



    @abstractmethod
    def getOptions(self) -> dict[ops.CMakeBaseOption,]:
        pass

    def validate(self):
        for option, value in self.__options__.items():
            if value is not None:
                if value.type != option.type:
                    raise ValueError('Invalid value type for option "' + option.name + '": ' + value.type)

        return
    
    def compile(self) -> list[str]:
        _args = []
        for option, value in self.__options__.items():
            compval = list(option.compile(value))
            _args += compval

        return _args

class CMakeConfigure(CMakeCommand):
    commandName: str = 'configure'
    __generators__ = [
        'Ninja', 
        'MinGW Makefiles', 
        'Visual Studio 16 2019', 
        'Visual Studio 17 2022',
        'Unix Makefiles'
        ]

    def getOptions(self) -> dict[ops.CMakeBaseOption,]:
        return {
            ops.CMakeSimpleOption('source_dir', '-S', '{option}{ssp}{value}', CMakeValType.STRING, '.'): None,
            ops.CMakeSimpleOption('build_dir', '-B', '{option}{ssp}{value}', CMakeValType.STRING, 'build'): None,
            ops.CMakeSimpleOption('generator', '-G', '{option}{ssp}{value}', CMakeValType.STRING, 'Ninja'): None,
            ops.CMakeOptionalSimpleOption('initial_cache', '-C', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeVariablesOption(): None,
            ops.CMakeVariablesOption(True): None,
            ops.CMakeOptionalSimpleOption('toolset_spec', '-T', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeOptionalSimpleOption('platform_name', '-A', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeOptionalSimpleOption('toolchain', '--toolchain', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeOptionalSimpleOption('install_prefix', '--install-prefix', '{option}{ssp}{value}', CMakeValType.STRING): None,
        }
    
class CMakeBuildCommand(CMakeCommand):
    commandName: str = 'build'

    def getOptions(self) -> dict[ops.CMakeBaseOption,]:
        return {
            ops.CMakeSimpleOption('build_path', '--build', '{option}{ssp}{value}', CMakeValType.STRING, '.'): None,
            ops.CMakeOptionalSimpleOption('max_jobs', '-j', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeOptionalSimpleOption('configuration', '--config', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeSwitchOption('verbose', '-v', False): None
        }
    
class CMakeInstallCommand(CMakeCommand):
    commandName: str = 'install'

    def getOptions(self) -> dict[CMakeBaseOption,]:
        return {
            ops.CMakeSimpleOption('install_path', '--install', '{option}{ssp}{value}', CMakeValType.STRING, '_install'): None,
            ops.CMakeOptionalSimpleOption('configuration', '--config', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeOptionalSimpleOption('component', '--component', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeOptionalSimpleOption('default_directory_permissions', '--default-directory-permissions', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeOptionalSimpleOption('prefix', '--prefix', '{option}{ssp}{value}', CMakeValType.STRING): None,
            ops.CMakeSwitchOption('verbose', '-v', False): None,
            ops.CMakeSwitchOption('strip', '--strip', False): None
        }